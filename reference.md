# Reference answers and traps

What a correct answer contains, and the mistakes the automatic checks look for. Use it while scoring
(README §6). Write down your expected answer before reading the models' answers: this file is that, written in
advance.

---

## A — Sharpe ratio

**Formula.** Annualised Sharpe ratio from daily returns:

> Sharpe = mean(daily excess return) / std(daily excess return) × √(trading days)
> where daily excess return = daily return − daily risk-free rate.

**Defensible conventions (all accepted):**

| Choice | Option 1 | Option 2 |
|---|---|---|
| Daily risk-free rate | `rf / days` (simple) | `(1 + rf) ** (1 / days) - 1` (compound) |
| Standard deviation | sample, `ddof=1` (most common) | population, `ddof=0` |
| Annual return (alternative) | arithmetic mean × days (above) | geometric `(1 + mean) ** days - 1`, then subtract `rf`, divide by std × √days |

The check reports which convention the code used. Saying which one it chose, in the docstring or a comment, is
part of a clear answer.

**Traps (the check flags them):**

- **Subtracting the annual rate from daily returns** (`mean(r) - 0.04`). The result is wildly negative
  (−112 on the test series). This is the convention error the test is built to catch.
- **Not annualising** (no √days).
- **Ignoring the `trading_days` parameter** (hard-coded 252). The check calls the function with `days = 12`.
- **Edge cases not handled.** Empty list or zero volatility that ends in `ZeroDivisionError`, `IndexError`,
  `StatisticsError`, `inf`, or `nan` with a NumPy warning. Handled means: raises a clear exception (e.g.
  `ValueError`) or returns `None` / `nan` on purpose.

**Test series used by the check:** `[0.01, -0.005, 0.007, 0.002, -0.003, 0.004, 0.006, -0.002]`, rf = 0.04.

| days | simple, ddof=1 | simple, ddof=0 | compound, ddof=1 | compound, ddof=0 |
|---|---|---|---|---|
| 252 | 6.6172 | 7.0741 | 6.6264 | 7.0840 |
| 12 | −0.6244 | −0.6675 | −0.5856 | −0.6260 |

Wrong: annual rf subtracted → −112.34; not annualised → 0.4168.

**Completeness:** type hints, a docstring, 2–3 unit tests, default of 252.

---

## B — Cumulative returns bug

**The bug.** Simple returns compound: the running value must be multiplied by `(1 + r)`, not increased by `r`.

```python
def cumulative_returns(daily_returns):
    cum = 1.0
    results = []
    for r in daily_returns:
        cum *= 1 + r
        results.append(cum - 1)
    return results
```

**Check:** `[0.1, -0.1, 0.05]` → `[0.10, -0.01, 0.0395]` (the buggy version gives `[0.10, 0.00, 0.05]`);
`[]` → `[]`. The explanation should say *compounding* or *multiply*. Note: the original hint comment
(`# <-- bug here`) was removed on purpose.

---

## C — Portfolio volatility, zero correlation

**Formula.** With zero correlation, variances add and the cross terms vanish:

> σ_p = √( Σ (w_i × σ_i)² )

**Trap:** `Σ w_i × σ_i`, which is the formula for **perfect** correlation. It overstates the volatility; the
check flags it. Zero correlation is itself a strong assumption that usually **understates** real portfolio risk;
an answer that says so in its comment is better than one that does not.

**Completeness:** standard library only (`math` is fine; no NumPy); a weights-sum check with a tolerance; a
no-negative-weights check; result printed to 4 decimal places; a comment explaining the assumption. The check
finds the model's own portfolio in its code and recomputes the expected value from it.

---

## D / E — Market order vs limit order (English / French)

**Content.**
- **Market order** (*ordre au marché*): executes at once at the best available price; execution is almost
  certain, the price is not.
- **Limit order** (*ordre à cours limité*): sets the worst acceptable price (a maximum to buy, a minimum to
  sell); the price is controlled, execution is not guaranteed.
- **A practical case for a limit order:** an illiquid share or a wide bid–ask spread; a volatile moment such as
  the open, or after news; a large order relative to the volume on screen.

**Instructions:** under 100 words (the check counts the whole answer); one situation; E entirely in French.
Precise French terms are a plus (*meilleure limite*, *fourchette*, *carnet d'ordres*).

**Trap:** saying a limit order executes "at exactly" the limit price. It executes at the limit **or better**.

---

## F — Grounded answer (the text is fictional)

1. The accumulation phase starts at 17:30 and lasts five minutes → **it ends at 17h35**. (The text never states
   17h35; the model has to add the five minutes.)
2. An unexecuted limit order **stays in the order book until the end of its validity** (*reste dans le carnet
   jusqu'à la fin de sa validité*).
3. **The text says nothing about fees** → the answer must say so. Any figure (€, %, basis points) is invented.

**Instructions:** at most three sentences; French; nothing beyond the text. Extra general knowledge about
closing auctions counts against *no extra content*, even if it is true.
