#!/usr/bin/env python3
"""Combine timings, automatic checks and blind scores into summary.md (and summary.csv) in the run folder.

Usage:  python3 summarize.py ~/dev/olala/results/run_YYYYMMDD_HHMM_gpu
Works without the blind scores too (the manual columns stay empty).
"""
import csv
import json
import os
import statistics
import sys


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run_dir = sys.argv[1]
    recs = [json.loads(l) for l in open(os.path.join(run_dir, "raw.jsonl")) if l.strip()]
    env = json.load(open(os.path.join(run_dir, "env.json"))) if os.path.exists(os.path.join(run_dir, "env.json")) else {}
    chk_path = os.path.join(run_dir, "checks.jsonl")
    checks = [json.loads(l) for l in open(chk_path)] if os.path.exists(chk_path) else []
    scores = {}
    sheet = os.path.join(run_dir, "blind", "scoring_sheet.csv")
    keyf = os.path.join(run_dir, "blind", "key.json")
    if os.path.exists(sheet) and os.path.exists(keyf):
        key = json.load(open(keyf))
        for row in csv.DictReader(open(sheet, newline="", encoding="utf-8-sig")):
            extra = row.pop(None, None)          # unquoted commas in notes -> extra columns
            if extra:
                print(f"note: row {row.get('code')} has commas in its notes; the extra text is ignored, scores are fine")
            vals = {}
            for k, v in row.items():
                if k and k.endswith("_0_5") and v and v.strip():
                    try:
                        vals[k] = float(v.strip().replace(",", "."))
                    except ValueError:
                        print(f"warning: {row.get('code')} {k}={v!r} is not a number; skipped")
            if vals and (row.get("code") or "").strip() in key:
                scores.setdefault(key[row["code"].strip()], []).append(vals)

    models = list(dict.fromkeys(r["model"] for r in recs))
    minfo = {m["name"]: m for m in env.get("models", [])}
    out = [f"# Olala test — summary ({env.get('backend', '?')} backend)", "",
           f"Run {os.path.basename(run_dir)} · host {env.get('host', '?')} · kernel {env.get('kernel', '?')} · "
           f"fork {env.get('fork_commit', '?')[:9]} · {env.get('samples', '?')} samples per prompt", "",
           "## Speed and memory", "",
           "| Model | Load s | GPU memory used (GTT, GiB) | Median gen tok/s | Median time to first token s "
           "| Median time to final answer s | Median total s | Truncated |",
           "|---|---|---|---|---|---|---|---|"]
    rows_csv = []
    for m in models:
        rs = [r for r in recs if r["model"] == m]
        i = minfo.get(m, {})
        gtt = None
        if i.get("gtt_loaded_bytes") is not None and i.get("gtt_before_bytes") is not None:
            gtt = round((i["gtt_loaded_bytes"] - i["gtt_before_bytes"]) / 2 ** 30, 2)
        def gen_tps(r):
            t = (r.get("timings") or {}).get("predicted_per_second")
            if t:
                return t
            n = (r.get("usage") or {}).get("completion_tokens")
            dt = (r.get("t_total_s") or 0) - (r.get("t_first_token_s") or 0)
            return n / dt if n and dt > 0 else None
        tps = med([gen_tps(r) for r in rs])
        ttft = med([r.get("t_first_token_s") for r in rs])
        ttfa = med([r.get("t_first_answer_s") for r in rs])
        tot = med([r.get("t_total_s") for r in rs])
        trunc = sum(r.get("finish_reason") == "length" for r in rs)
        out.append(f"| {m} | {i.get('load_s', '?')} | {gtt if gtt is not None else '–'} | {tps} | {ttft} | {ttfa} | {tot} | {trunc}/{len(rs)} |")
        rows_csv.append({"model": m, "gen_tok_s": tps, "ttft_s": ttft, "time_to_answer_s": ttfa, "total_s": tot,
                         "gtt_gib": gtt, "truncated": trunc})

    out += ["", "Time to first token includes thinking; time to final answer is when the first answer token "
            "arrives (after any thinking). Only Olala thinks in this run (runbook D6).", "",
            "## Time to final answer by prompt (median s)", "",
            "| Model | " + " | ".join(sorted({r['prompt'] for r in recs})) + " |",
            "|---|" + "---|" * len({r['prompt'] for r in recs})]
    for m in models:
        cells = [str(med([r.get("t_first_answer_s") for r in recs if r["model"] == m and r["prompt"] == p]))
                 for p in sorted({r['prompt'] for r in recs})]
        out.append(f"| {m} | " + " | ".join(cells) + " |")

    if checks:
        out += ["", "## Automatic checks (samples passing)", "",
                "| Model | " + " | ".join(f"{p} correct / complete" for p in sorted({c['prompt'] for c in checks})) + " |",
                "|---|" + "---|" * len({c['prompt'] for c in checks})]
        for m in models:
            cells = []
            for p in sorted({c["prompt"] for c in checks}):
                cs = [c for c in checks if c["model"] == m and c["prompt"] == p]
                cor = "–" if p in ("D", "E") else str(sum(bool(c.get("PASS_correct")) for c in cs))
                cells.append(f"{cor} / {sum(bool(c.get('PASS_complete')) for c in cs)} of {len(cs)}")
            out.append(f"| {m} | " + " | ".join(cells) + " |")
        conv = [c for c in checks if c["prompt"] == "A"]
        if conv:
            out += ["", "**Prompt A — Sharpe convention used** (sample by sample):", ""]
            for m in models:
                out.append(f"- {m}: " + "; ".join(str(c.get("convention_252", c.get("call_error", "no function")))
                                                   for c in conv if c["model"] == m))

    if scores:
        crit = ["correctness_0_5", "completeness_0_5", "clarity_0_5", "no_extra_content_0_5"]
        out += ["", "## Blind scores (sample 1, mean over prompts, 0–5, 5 best)", "",
                "| Model | " + " | ".join(c.replace("_0_5", "") for c in crit) + " | answers scored |",
                "|---|" + "---|" * (len(crit) + 1)]
        for m in models:
            ss = scores.get(m, [])
            cells = [str(round(statistics.mean([s[c] for s in ss if c in s]), 2)) if any(c in s for s in ss) else "–"
                     for c in crit]
            out.append(f"| {m} | " + " | ".join(cells) + f" | {len(ss)} |")

    out += ["", "Limits: one machine, one run, few samples; automatic checks are partly heuristic (README §5); "
            "one scorer. Not a benchmark."]
    with open(os.path.join(run_dir, "summary.md"), "w") as f:
        f.write("\n".join(out) + "\n")
    if rows_csv:
        with open(os.path.join(run_dir, "summary.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows_csv[0].keys()))
            w.writeheader()
            w.writerows(rows_csv)
    print(f"Wrote {os.path.join(run_dir, 'summary.md')}")


if __name__ == "__main__":
    main()
