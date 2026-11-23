#!/usr/bin/env python3
"""Automatic checks on the answers in a run folder.

Runs the code the models wrote (prompts A, B, C) in a separate Python process with a timeout, against reference
values, and applies simple text checks to D, E and F. Writes checks.jsonl and checks.md in the run folder.

Usage:  ~/dev/ml-env/bin/python check_answers.py ~/dev/olala/results/run_YYYYMMDD_HHMM_gpu
(Use the ml-env Python: a model may import numpy in prompt A.)

The model code runs as your user, in a temporary folder, with a 30 s limit. It is code you have not reviewed:
read checks.md before trusting a result, and do not run this on answers from an unknown source.
"""
import json
import math
import os
import re
import subprocess
import sys
import tempfile

HARNESS_COMMON = r'''
import importlib.util, io, json, contextlib, inspect, math, sys, warnings, unittest
CAND = sys.argv[1]
res = {}
spec = importlib.util.spec_from_file_location("candidate", CAND)
mod = importlib.util.module_from_spec(spec)
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        spec.loader.exec_module(mod)
    res["import_ok"] = True
except SystemExit as e:
    res["import_ok"] = True
    res["note"] = "module called sys.exit at import (e.g. unittest.main() without a __main__ guard)"
except BaseException as e:
    res["import_ok"] = False
    res["import_error"] = repr(e)[:300]

def own_tests():
    n = ok = 0
    for name, obj in list(vars(mod).items()):
        if name.startswith("test") and inspect.isfunction(obj) and getattr(obj, "__module__", "") == "candidate":
            try:
                if len(inspect.signature(obj).parameters) == 0:
                    n += 1
                    with contextlib.redirect_stdout(io.StringIO()):
                        obj()
                    ok += 1
            except BaseException:
                pass
    loader = unittest.TestLoader()
    for name, obj in list(vars(mod).items()):
        if inspect.isclass(obj) and issubclass(obj, unittest.TestCase) and obj.__module__ == "candidate":
            suite = loader.loadTestsFromTestCase(obj)
            r = unittest.TestResult()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                suite.run(r)
            n += r.testsRun
            ok += r.testsRun - len(r.failures) - len(r.errors)
    return n, ok

def main_asserts(res):
    """Tests written as asserts under `if __name__ == "__main__":` (not functions): count them and run the file."""
    import ast, subprocess
    try:
        tree = ast.parse(open(CAND).read())
    except SyntaxError:
        return
    n = 0
    for node in tree.body:
        if isinstance(node, ast.If) and "__main__" in ast.dump(node.test):
            n += sum(isinstance(x, ast.Assert) for x in ast.walk(node))
    res["main_block_asserts"] = n
    if n:
        p = subprocess.run([sys.executable, "-I", CAND], capture_output=True, text=True, timeout=20)
        res["main_block_passes"] = p.returncode == 0
        if p.returncode != 0:
            res["main_block_error"] = (p.stderr or "").strip().splitlines()[-1][:200] if p.stderr else "exit %d" % p.returncode

def find_func(*keys):
    for name, obj in vars(mod).items():
        if inspect.isfunction(obj) and getattr(obj, "__module__", "") == "candidate" and not name.startswith("test"):
            if any(k in name.lower() for k in keys):
                return name, obj
    return None, None

def classify_edge(f, *a):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                v = f(*a)
        except Exception as e:
            import traceback
            last = traceback.extract_tb(e.__traceback__)[-1]
            explicit = last.filename == CAND and (last.line or "").strip().startswith("raise")
            if explicit:
                return "handled: raises " + e.__class__.__name__ + " explicitly"
            if isinstance(e, (ZeroDivisionError, IndexError)) or e.__class__.__name__ == "StatisticsError":
                return "unhandled: " + e.__class__.__name__
            return "handled: raises " + e.__class__.__name__
    try:
        fv = float(v) if v is not None else None
    except Exception:
        fv = None
    if v is None:
        return "handled: returns None"
    if fv is not None and math.isinf(fv):
        return "unhandled: returns inf"
    if fv is not None and math.isnan(fv):
        return "unhandled: nan with warning" if w else "handled: returns nan"
    return f"handled: returns {v!r}"
'''

HARNESS_A = HARNESS_COMMON + r'''
import statistics
R = [0.01, -0.005, 0.007, 0.002, -0.003, 0.004, 0.006, -0.002]
RF = 0.04
def variants(days):
    out = {}
    for conv, rd in (("simple rf/days", RF / days), ("compound (1+rf)^(1/days)-1", (1 + RF) ** (1 / days) - 1)):
        ex = [r - rd for r in R]
        m = sum(ex) / len(ex)
        for ddof in (1, 0):
            s = math.sqrt(sum((x - m) ** 2 for x in ex) / (len(ex) - ddof))
            out[f"{conv}, std ddof={ddof}"] = m / s * math.sqrt(days)
    m = sum(R) / len(R)
    s1 = statistics.stdev(R)
    out["ALT geometric annual return"] = ((1 + m) ** days - 1 - RF) / (s1 * math.sqrt(days))
    out["WRONG annual rf subtracted from daily returns"] = (m - RF) / s1 * math.sqrt(days)
    out["WRONG not annualised"] = (m - RF / days) / s1
    return out
def match(v, days):
    for k, e in variants(days).items():
        if v is not None and abs(v - e) <= 1e-6 * max(1.0, abs(e)):
            return k
    return "no known convention"
name, f = find_func("sharpe")
res["function"] = name
if f:
    try:
        sig = inspect.signature(f)
        res["has_default_252"] = any(p.default == 252 for p in sig.parameters.values())
        res["type_hints"] = all(p.annotation is not inspect._empty for p in sig.parameters.values())
        res["docstring"] = bool(inspect.getdoc(f))
    except Exception:
        pass
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            v252 = float(f(R, RF, 252))
        res["value_252"] = v252
        res["convention_252"] = match(v252, 252)
    except Exception as e:
        res["call_error"] = repr(e)[:200]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            vdef = float(f(R, RF))
        res["default_matches_252"] = abs(vdef - res.get("value_252", float("nan"))) < 1e-12
    except Exception as e:
        res["default_error"] = repr(e)[:200]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            v12 = float(f(R, RF, 12))
        res["convention_days12"] = match(v12, 12)
    except Exception as e:
        res["days12_error"] = repr(e)[:200]
    res["edge_empty"] = classify_edge(f, [], RF)
    res["edge_zero_vol"] = classify_edge(f, [0.25, 0.25, 0.25, 0.25], RF)
n, ok = own_tests()
res["own_tests_found"], res["own_tests_passed"] = n, ok
main_asserts(res)
print("@@RESULT@@" + json.dumps(res))
'''

HARNESS_B = HARNESS_COMMON + r'''
name, f = find_func("cumulative_returns", "cumul")
res["function"] = name
if f:
    exp = []
    c = 1.0
    for r in [0.1, -0.1, 0.05]:
        c *= 1 + r
        exp.append(c - 1)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            got = [float(x) for x in f([0.1, -0.1, 0.05])]
        res["got"] = got
        res["correct"] = len(got) == 3 and all(abs(a - b) < 1e-9 for a, b in zip(got, exp))
        res["still_additive"] = len(got) == 3 and all(abs(a - b) < 1e-9 for a, b in zip(got, [0.1, 0.0, 0.05]))
    except Exception as e:
        res["call_error"] = repr(e)[:200]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            res["empty_ok"] = list(f([])) == []
    except Exception as e:
        res["empty_ok"] = False
print("@@RESULT@@" + json.dumps(res))
'''

HARNESS_C = r'''
import ast, io, json, math, re, runpy, sys, contextlib
CAND = sys.argv[1]
res = {}
src = open(CAND).read()
try:
    tree = ast.parse(src)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            mods.add(node.module.split(".")[0])
    res["non_stdlib_imports"] = sorted(m for m in mods if m not in sys.stdlib_module_names)
except SyntaxError as e:
    res["syntax_error"] = str(e)[:200]
buf = io.StringIO()
g = {}
try:
    with contextlib.redirect_stdout(buf):
        g = runpy.run_path(CAND, run_name="__main__")
    res["ran_ok"] = True
except SystemExit as e:
    res["ran_ok"] = e.code in (0, None)
except BaseException as e:
    res["ran_ok"] = False
    res["run_error"] = repr(e)[:300]
out = buf.getvalue()
res["stdout_tail"] = out[-300:]
port = None
for k, v in g.items():
    if isinstance(v, list) and v and all(isinstance(x, dict) and "weight" in x and "daily_vol" in x for x in v):
        port = v
        res["portfolio_var"] = k
        break
if port is None:
    m = re.search(r"\[\s*\{[^\]]*?\"weight\"[^\]]*\]", src, re.S)
    if m:
        try:
            port = ast.literal_eval(m.group(0))
            res["portfolio_var"] = "(parsed from source)"
        except Exception:
            pass
if port:
    exp = math.sqrt(sum((float(a["weight"]) * float(a["daily_vol"])) ** 2 for a in port))
    perfect = sum(float(a["weight"]) * float(a["daily_vol"]) for a in port)
    res["expected"] = round(exp, 4)
    nums = [float(x) for x in re.findall(r"-?\d+\.\d+", out)]
    pct = [x / 100 for x in nums]
    res["printed_expected"] = any(abs(x - exp) < 5e-5 for x in nums) or any(abs(x - exp) < 5e-5 for x in pct)
    res["printed_4dp"] = bool(re.search(r"\b%s\b" % re.escape(f"{exp:.4f}"), out))
    res["printed_perfect_correlation"] = (abs(perfect - exp) > 1e-4) and any(abs(x - perfect) < 5e-5 for x in nums)
low = src.lower()
res["comment_mentions_correlation"] = any("correl" in line.lower() for line in src.splitlines()
                                          if line.strip().startswith("#")) or ('"""' in src and "correl" in low)
res["has_weight_sum_check"] = bool(re.search(r"(isclose|abs\(|tol|toler)", low)) and "sum" in low and "weight" in low
res["has_negative_check"] = bool(re.search(r"<\s*0(?![.\d]*[1-9])|negative|>=\s*0(?![.\d]*[1-9])|\b0(\.0+)?\s*<=|min\(", low))
print("@@RESULT@@" + json.dumps(res))
'''


def code_blocks(text):
    blocks = re.findall(r"```(?:python|py)?[ \t]*\n(.*?)```", text, re.S | re.I)
    return [b for b in blocks if b.strip()]


def run_harness(harness, code, timeout=30):
    with tempfile.TemporaryDirectory() as d:
        cand = os.path.join(d, "candidate.py")
        hp = os.path.join(d, "harness.py")
        with open(cand, "w") as f:
            f.write(code)
        with open(hp, "w") as f:
            f.write(harness)
        try:
            p = subprocess.run([sys.executable, "-I", hp, cand], cwd=d, capture_output=True, text=True,
                               timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"timeout": True}
        m = re.search(r"@@RESULT@@(.*)$", p.stdout, re.M)
        if not m:
            return {"harness_failed": True, "stderr": (p.stderr or "")[-400:]}
        return json.loads(m.group(1))


def best_code_result(harness, content, ok_key):
    blocks = code_blocks(content)
    if not blocks:
        return {"no_code_block": True}
    tries = ["\n\n".join(blocks)] + blocks
    first = None
    for code in tries:
        r = run_harness(harness, code)
        first = first or r
        if r.get(ok_key):
            return r
    return first


def words(text):
    text = re.sub(r"[*_#`>|]", " ", text)
    return [w for w in re.split(r"\s+", text) if re.search(r"\w", w)]


FR = {"le", "la", "les", "un", "une", "des", "est", "et", "en", "au", "du", "que", "qui", "pour", "pas", "dans", "à"}
EN = {"the", "a", "an", "is", "and", "in", "of", "to", "that", "for", "not", "at", "it", "with", "when"}


def lang_guess(text):
    ws = [w.lower().strip(".,;:!?()«»\"'") for w in words(text)]
    fr = sum(w in FR for w in ws)
    en = sum(w in EN for w in ws)
    return "fr" if fr > en else "en" if en > fr else "?"


def sentences(text):
    t = re.sub(r"^\s*(\d+[.)]|[-*•])\s+", "", text, flags=re.M)
    parts = [s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if re.search(r"\w", s)]
    return len(parts)


def check(rec):
    c = rec.get("content") or ""
    p = rec["prompt"]
    out = {"model": rec["model"], "prompt": p, "sample": rec["sample"],
           "truncated": rec.get("finish_reason") == "length", "error": rec.get("error")}
    if p == "A":
        r = best_code_result(HARNESS_A, c, "value_252")
        out.update(r)
        conv = r.get("convention_252", "")
        # correct = a known, defensible convention at 252 days, and the same convention when days=12
        # (proves the third parameter is really used, not hard-coded)
        out["PASS_correct"] = bool(conv) and not conv.startswith(("WRONG", "no known")) \
            and r.get("convention_days12") == conv
        out["PASS_edges"] = str(r.get("edge_empty", "")).startswith("handled") and \
            str(r.get("edge_zero_vol", "")).startswith("handled")
        out["PASS_complete"] = bool(r.get("type_hints")) and bool(r.get("docstring")) and \
            (r.get("own_tests_found", 0) >= 2 or r.get("main_block_asserts", 0) >= 2) and \
            bool(r.get("has_default_252"))
        out["tests_note"] = ("tests as functions/TestCase: %s; asserts in __main__: %s"
                             % (r.get("own_tests_found", 0), r.get("main_block_asserts", 0)))
    elif p == "B":
        r = best_code_result(HARNESS_B, c, "correct")
        out.update(r)
        prose = re.sub(r"```.*?```", " ", c, flags=re.S).lower()
        out["explains_compounding"] = bool(re.search(r"compound|multipl|product|\(1 ?\+ ?r\)|1 \+ r", prose))
        out["PASS_correct"] = bool(r.get("correct")) and bool(r.get("empty_ok"))
        out["PASS_complete"] = out["PASS_correct"] and out["explains_compounding"]
    elif p == "C":
        blocks = code_blocks(c)
        r = run_harness(HARNESS_C, max(blocks, key=len)) if blocks else {"no_code_block": True}
        out.update(r)
        out["PASS_correct"] = bool(r.get("printed_expected")) and not r.get("printed_perfect_correlation")
        out["PASS_complete"] = out["PASS_correct"] and r.get("non_stdlib_imports") == [] and \
            bool(r.get("printed_4dp")) and bool(r.get("comment_mentions_correlation")) and \
            bool(r.get("has_weight_sum_check")) and bool(r.get("has_negative_check"))
    elif p in ("D", "E"):
        n = len(words(c))
        out["words"] = n
        out["lang"] = lang_guess(c)
        out["PASS_complete"] = n < 100 and out["lang"] == ("en" if p == "D" else "fr")
        out["note"] = "Word count covers the whole answer, including the practical situation."
    elif p == "F":
        low = c.lower()
        out["q1_17h35"] = bool(re.search(r"17\s*[h:]\s*35", low))
        out["q2_stays_in_book"] = "carnet" in low and ("validit" in low or "expir" in low)
        out["q3_says_not_in_text"] = bool(re.search(
            r"ne (le )?(pr[ée]cise|mentionne|dit|indique|permet|parle|donne|sp[ée]cifie)|aucune (information|mention|indication)"
            r"|pas (d['’]information|mentionn|pr[ée]cis|indiqu)|n['’]est pas (pr[ée]cis|mentionn|indiqu)|non (pr[ée]cis|mentionn|indiqu)",
            low))
        out["invents_fee"] = bool(re.search(r"\d+([.,]\d+)?\s*(€|eur|euros?|%|centimes?|bps|points? de base)", low))
        out["sentences"] = sentences(c)
        out["lang"] = lang_guess(c)
        out["PASS_correct"] = out["q1_17h35"] and out["q2_stays_in_book"] and out["q3_says_not_in_text"] \
            and not out["invents_fee"]
        out["PASS_complete"] = out["PASS_correct"] and out["sentences"] <= 3 and out["lang"] == "fr"
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run_dir = sys.argv[1]
    recs = [json.loads(l) for l in open(os.path.join(run_dir, "raw.jsonl")) if l.strip()]
    results = []
    for i, rec in enumerate(recs, 1):
        print(f"[{i}/{len(recs)}] {rec['model']} {rec['prompt']} s{rec['sample']}", flush=True)
        results.append(check(rec))
    with open(os.path.join(run_dir, "checks.jsonl"), "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    models = sorted({r["model"] for r in results})
    prompts = sorted({r["prompt"] for r in results})
    lines = ["# Automatic checks", "",
             "Each cell: samples passing / samples run. 'correct' = the reference test; 'complete' = every "
             "instruction the check can see. Heuristic checks are listed in README §5 — read the details below "
             "before quoting a cell.", "",
             "| Prompt | " + " | ".join(f"{m} correct | {m} complete" for m in models) + " |",
             "|---|" + "---|---|" * len(models)]
    for p in prompts:
        row = [p]
        for m in models:
            rs = [r for r in results if r["model"] == m and r["prompt"] == p]
            c = sum(bool(r.get("PASS_correct")) for r in rs) if p not in ("D", "E") else None
            k = sum(bool(r.get("PASS_complete")) for r in rs)
            row += [f"{c}/{len(rs)}" if c is not None else "n/a", f"{k}/{len(rs)}"]
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Details", ""]
    skip = {"model", "prompt", "sample", "stdout_tail"}
    for r in results:
        lines.append(f"- **{r['model']} {r['prompt']} s{r['sample']}**: " +
                     "; ".join(f"{k}={v}" for k, v in r.items()
                               if k not in skip and (k.startswith("PASS_") or v not in (None, False, [], ""))))
    with open(os.path.join(run_dir, "checks.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {os.path.join(run_dir, 'checks.md')}")
    print(f"Next: python3 make_blind.py {run_dir}")


if __name__ == "__main__":
    main()
