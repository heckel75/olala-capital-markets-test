#!/usr/bin/env python3
"""Make a blind scoring packet from a run folder.

For each prompt, takes sample 1 of every model, shuffles them and labels them A1/A2/A3, B1/B2/B3, ... so you
score without knowing which model wrote which answer. Only the final answer is shown (the reasoning would reveal
the model). Writes, inside the run folder:

  blind/scoring_packet.md   read this while scoring
  blind/scoring_sheet.csv   fill in the scores (any spreadsheet or text editor)
  blind/key.json            which code is which model: do NOT open until scoring is finished

Usage:  python3 make_blind.py ~/dev/olala/results/run_YYYYMMDD_HHMM_gpu
"""
import csv
import json
import os
import random
import sys


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run_dir = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    prompts = {p["id"]: p for p in json.load(open(os.path.join(here, "prompts.json")))}
    recs = [json.loads(l) for l in open(os.path.join(run_dir, "raw.jsonl")) if l.strip()]
    recs = [r for r in recs if r["sample"] == 1]
    bdir = os.path.join(run_dir, "blind")
    if os.path.exists(os.path.join(bdir, "key.json")):
        sys.exit(f"{bdir}/key.json already exists: delete the blind folder first if you really want a new shuffle.")
    os.makedirs(bdir, exist_ok=True)
    rng = random.SystemRandom()
    key, packet, rows = {}, ["# Blind scoring packet", "",
                             "Score each answer on the sheet. Do not open key.json until you have finished.", ""], []
    for pid in sorted({r["prompt"] for r in recs}):
        group = [r for r in recs if r["prompt"] == pid]
        rng.shuffle(group)
        packet += [f"## Prompt {pid}: {prompts[pid]['title']}", "", "**Prompt:**", "", "```text",
                   prompts[pid]["text"], "```", ""]
        for i, r in enumerate(group, 1):
            code = f"{pid}{i}"
            key[code] = r["model"]
            packet += [f"### {code}", "", (r.get("content") or "*(empty answer)*").strip(), "", "---", ""]
            rows.append({"code": code, "prompt": pid, "correctness_0_5": "", "completeness_0_5": "",
                         "clarity_0_5": "", "no_extra_content_0_5": "", "notes": ""})
    with open(os.path.join(bdir, "scoring_packet.md"), "w") as f:
        f.write("\n".join(packet))
    with open(os.path.join(bdir, "scoring_sheet.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(bdir, "key.json"), "w") as f:
        json.dump(key, f, indent=2)
    print(f"Wrote {bdir}/scoring_packet.md and scoring_sheet.csv ({len(rows)} answers to score).")
    print("Scale (5 is always best): correctness, completeness (every instruction followed), clarity / code "
          "quality, no_extra_content (5 = nothing invented or unnecessary). See README §6.")
    print(f"When done: python3 summarize.py {run_dir}")


if __name__ == "__main__":
    main()
