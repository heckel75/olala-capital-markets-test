# Olala test — summary (gpu backend)

Run run_20261120_1417_gpu · host a9mega · kernel 7.0.0-43-generic · fork 55c22dca0 · 3 samples per prompt

## Speed and memory

| Model | Load s | GPU memory used (GTT, GiB) | Median gen tok/s | Median time to first token s | Median time to final answer s | Median total s | Truncated |
|---|---|---|---|---|---|---|---|
| olala-mini-7a1b | 2.0 | 6.87 | 61.2 | 0.1 | 9.2 | 12.6 | 0/18 |
| phi-4-mini | 2.0 | 5.02 | 46.1 | 0.0 | 0.0 | 3.6 | 0/18 |
| qwen3.5-9b | 2.0 | 8.51 | 23.9 | 0.1 | 0.1 | 8.1 | 0/18 |

Time to first token includes thinking; time to final answer is when the first answer token arrives (after any thinking). Only Olala thinks in this run (runbook D6).

## Time to final answer by prompt (median s)

| Model | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| olala-mini-7a1b | 25.5 | 8.0 | 9.7 | 8.1 | 9.0 | 8.5 |
| phi-4-mini | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| qwen3.5-9b | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |

## Automatic checks (samples passing)

| Model | A correct / complete | B correct / complete | C correct / complete | D correct / complete | E correct / complete | F correct / complete |
|---|---|---|---|---|---|---|
| olala-mini-7a1b | 2 / 0 of 3 | 3 / 3 of 3 | 3 / 3 of 3 | – / 3 of 3 | – / 2 of 3 | 2 / 2 of 3 |
| phi-4-mini | 0 / 0 of 3 | 2 / 2 of 3 | 3 / 3 of 3 | – / 3 of 3 | – / 2 of 3 | 0 / 0 of 3 |
| qwen3.5-9b | 3 / 2 of 3 | 3 / 3 of 3 | 2 / 2 of 3 | – / 3 of 3 | – / 1 of 3 | 3 / 3 of 3 |

**Prompt A — Sharpe convention used** (sample by sample):

- olala-mini-7a1b: simple rf/days, std ddof=1; simple rf/days, std ddof=1; WRONG annual rf subtracted from daily returns
- phi-4-mini: no known convention; no known convention; no known convention
- qwen3.5-9b: simple rf/days, std ddof=0; simple rf/days, std ddof=1; simple rf/days, std ddof=1

## Blind scores (sample 1, mean over prompts, 0–5, 5 best)

| Model | correctness | completeness | clarity | no_extra_content | answers scored |
|---|---|---|---|---|---|
| olala-mini-7a1b | 3.67 | 4.67 | 4.17 | 3.33 | 6 |
| phi-4-mini | 2.67 | 4.83 | 3.83 | 3.17 | 6 |
| qwen3.5-9b | 3.67 | 4.83 | 4.17 | 3.5 | 6 |

Limits: one machine, one run, few samples; automatic checks are partly heuristic (README §5); one scorer. Not a benchmark.
