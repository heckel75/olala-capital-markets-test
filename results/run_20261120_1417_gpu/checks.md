# Automatic checks

Each cell: samples passing / samples run. 'correct' = the reference test; 'complete' = every instruction the check can see. Heuristic checks are listed in README §5 — read the details below before quoting a cell.

| Prompt | olala-mini-7a1b correct | olala-mini-7a1b complete | phi-4-mini correct | phi-4-mini complete | qwen3.5-9b correct | qwen3.5-9b complete |
|---|---|---|---|---|---|---|
| A | 2/3 | 0/3 | 0/3 | 0/3 | 3/3 | 2/3 |
| B | 3/3 | 3/3 | 2/3 | 2/3 | 3/3 | 3/3 |
| C | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 | 2/3 |
| D | n/a | 3/3 | n/a | 3/3 | n/a | 3/3 |
| E | n/a | 2/3 | n/a | 2/3 | n/a | 1/3 |
| F | 2/3 | 2/3 | 0/3 | 0/3 | 3/3 | 3/3 |

## Details

- **olala-mini-7a1b A s1**: import_error=ModuleNotFoundError("No module named 'your_module'"); function=sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=6.617233552133719; convention_252=simple rf/days, std ddof=1; default_matches_252=True; convention_days12=simple rf/days, std ddof=1; edge_empty=handled: raises ValueError explicitly; edge_zero_vol=unhandled: ZeroDivisionError; PASS_correct=True; PASS_edges=False; PASS_complete=False; tests_note=tests as functions/TestCase: 0; asserts in __main__: 0
- **olala-mini-7a1b A s2**: import_ok=True; function=sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=6.61723355213372; convention_252=simple rf/days, std ddof=1; default_matches_252=True; convention_days12=simple rf/days, std ddof=1; edge_empty=handled: raises ValueError explicitly; edge_zero_vol=handled: raises ZeroDivisionError explicitly; PASS_correct=True; PASS_edges=True; PASS_complete=False; tests_note=tests as functions/TestCase: 0; asserts in __main__: 0
- **olala-mini-7a1b A s3**: import_ok=True; function=sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=-112.33894346384218; convention_252=WRONG annual rf subtracted from daily returns; default_matches_252=True; convention_days12=WRONG annual rf subtracted from daily returns; edge_empty=handled: raises ValueError explicitly; edge_zero_vol=handled: raises ValueError explicitly; PASS_correct=False; PASS_edges=True; PASS_complete=False; tests_note=tests as functions/TestCase: 0; asserts in __main__: 0
- **olala-mini-7a1b B s1**: import_ok=True; function=cumulative_returns; got=[0.10000000000000009, -0.009999999999999898, 0.03950000000000009]; correct=True; empty_ok=True; explains_compounding=True; PASS_correct=True; PASS_complete=True
- **olala-mini-7a1b B s2**: import_ok=True; function=cumulative_returns; got=[0.10000000000000009, -0.009999999999999898, 0.03950000000000009]; correct=True; empty_ok=True; explains_compounding=True; PASS_correct=True; PASS_complete=True
- **olala-mini-7a1b B s3**: import_ok=True; function=cumulative_returns; got=[0.10000000000000009, -0.009999999999999898, 0.03950000000000009]; correct=True; empty_ok=True; explains_compounding=True; PASS_correct=True; PASS_complete=True
- **olala-mini-7a1b C s1**: ran_ok=True; portfolio_var=portfolio; expected=0.0094; printed_expected=True; printed_4dp=True; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=True; PASS_complete=True
- **olala-mini-7a1b C s2**: ran_ok=True; portfolio_var=portfolio; expected=0.0088; printed_expected=True; printed_4dp=True; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=True; PASS_complete=True
- **olala-mini-7a1b C s3**: ran_ok=True; portfolio_var=portfolio; expected=0.0124; printed_expected=True; printed_4dp=True; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=True; PASS_complete=True
- **olala-mini-7a1b D s1**: words=71; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **olala-mini-7a1b D s2**: words=84; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **olala-mini-7a1b D s3**: words=73; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **olala-mini-7a1b E s1**: words=114; lang=fr; PASS_complete=False; note=Word count covers the whole answer, including the practical situation.
- **olala-mini-7a1b E s2**: words=72; lang=fr; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **olala-mini-7a1b E s3**: words=53; lang=fr; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **olala-mini-7a1b F s1**: q2_stays_in_book=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=False; PASS_complete=False
- **olala-mini-7a1b F s2**: q1_17h35=True; q2_stays_in_book=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=True; PASS_complete=True
- **olala-mini-7a1b F s3**: q1_17h35=True; q2_stays_in_book=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=True; PASS_complete=True
- **phi-4-mini A s1**: import_error=AssertionError(); function=calculate_sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=0.028071905669330502; convention_252=no known convention; default_matches_252=True; convention_days12=no known convention; edge_empty=handled: raises ValueError explicitly; edge_zero_vol=handled: raises ValueError explicitly; own_tests_found=1; PASS_correct=False; PASS_edges=True; PASS_complete=False; tests_note=tests as functions/TestCase: 1; asserts in __main__: 0
- **phi-4-mini A s2**: import_error=AssertionError(); function=calculate_sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=0.44624704568781676; convention_252=no known convention; default_matches_252=True; convention_days12=no known convention; edge_empty=handled: raises ValueError explicitly; edge_zero_vol=handled: raises ValueError explicitly; own_tests_found=1; PASS_correct=False; PASS_edges=True; PASS_complete=False; tests_note=tests as functions/TestCase: 1; asserts in __main__: 0
- **phi-4-mini A s3**: import_error=AssertionError(); function=calculate_sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=0.44624704568781676; convention_252=no known convention; default_matches_252=True; convention_days12=no known convention; edge_empty=handled: raises ValueError explicitly; edge_zero_vol=handled: raises ValueError explicitly; own_tests_found=1; PASS_correct=False; PASS_edges=True; PASS_complete=False; tests_note=tests as functions/TestCase: 1; asserts in __main__: 0
- **phi-4-mini B s1**: import_ok=True; function=cumulative_returns; got=[1.1, 0.9900000000000001, 1.0395]; empty_ok=True; explains_compounding=True; PASS_correct=False; PASS_complete=False
- **phi-4-mini B s2**: import_ok=True; function=cumulative_returns; got=[0.10000000000000009, -0.009999999999999898, 0.03950000000000009]; correct=True; empty_ok=True; explains_compounding=True; PASS_correct=True; PASS_complete=True
- **phi-4-mini B s3**: import_ok=True; function=cumulative_returns; got=[0.10000000000000009, -0.009999999999999898, 0.03950000000000009]; correct=True; empty_ok=True; explains_compounding=True; PASS_correct=True; PASS_complete=True
- **phi-4-mini C s1**: ran_ok=True; portfolio_var=portfolio; expected=0.0113; printed_expected=True; printed_4dp=True; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=True; PASS_complete=True
- **phi-4-mini C s2**: ran_ok=True; portfolio_var=portfolio; expected=0.0113; printed_expected=True; printed_4dp=True; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=True; PASS_complete=True
- **phi-4-mini C s3**: ran_ok=True; portfolio_var=portfolio; expected=0.0113; printed_expected=True; printed_4dp=True; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=True; PASS_complete=True
- **phi-4-mini D s1**: words=67; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **phi-4-mini D s2**: words=75; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **phi-4-mini D s3**: words=75; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **phi-4-mini E s1**: words=100; lang=fr; PASS_complete=False; note=Word count covers the whole answer, including the practical situation.
- **phi-4-mini E s2**: words=77; lang=fr; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **phi-4-mini E s3**: words=77; lang=fr; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **phi-4-mini F s1**: q1_17h35=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=False; PASS_complete=False
- **phi-4-mini F s2**: q1_17h35=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=False; PASS_complete=False
- **phi-4-mini F s3**: q1_17h35=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=False; PASS_complete=False
- **qwen3.5-9b A s1**: import_ok=True; function=calculate_sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=7.074120228671284; convention_252=simple rf/days, std ddof=0; default_matches_252=True; convention_days12=simple rf/days, std ddof=0; edge_empty=handled: raises ValueError explicitly; edge_zero_vol=handled: raises ValueError explicitly; own_tests_found=1; PASS_correct=True; PASS_edges=True; PASS_complete=False; tests_note=tests as functions/TestCase: 1; asserts in __main__: 0
- **qwen3.5-9b A s2**: import_ok=True; function=calculate_sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=6.617233552133719; convention_252=simple rf/days, std ddof=1; default_matches_252=True; convention_days12=simple rf/days, std ddof=1; edge_empty=handled: raises ValueError explicitly; edge_zero_vol=handled: raises ValueError explicitly; own_tests_found=3; own_tests_passed=2; PASS_correct=True; PASS_edges=True; PASS_complete=True; tests_note=tests as functions/TestCase: 3; asserts in __main__: 0
- **qwen3.5-9b A s3**: import_ok=True; function=calculate_sharpe_ratio; has_default_252=True; type_hints=True; docstring=True; value_252=6.617233552133719; convention_252=simple rf/days, std ddof=1; default_matches_252=True; convention_days12=simple rf/days, std ddof=1; edge_empty=handled: returns 0.0; edge_zero_vol=handled: returns 0.0; main_block_asserts=5; main_block_passes=True; PASS_correct=True; PASS_edges=True; PASS_complete=True; tests_note=tests as functions/TestCase: 0; asserts in __main__: 5
- **qwen3.5-9b B s1**: import_ok=True; function=cumulative_returns; got=[0.10000000000000009, -0.009999999999999898, 0.03950000000000009]; correct=True; empty_ok=True; explains_compounding=True; PASS_correct=True; PASS_complete=True
- **qwen3.5-9b B s2**: import_ok=True; function=cumulative_returns; got=[0.10000000000000009, -0.009999999999999898, 0.03950000000000009]; correct=True; empty_ok=True; explains_compounding=True; PASS_correct=True; PASS_complete=True
- **qwen3.5-9b B s3**: import_ok=True; function=cumulative_returns; got=[0.10000000000000009, -0.009999999999999898, 0.03950000000000009]; correct=True; empty_ok=True; explains_compounding=True; PASS_correct=True; PASS_complete=True
- **qwen3.5-9b C s1**: ran_ok=True; portfolio_var=(parsed from source); expected=0.0103; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=False; PASS_complete=False
- **qwen3.5-9b C s2**: ran_ok=True; portfolio_var=(parsed from source); expected=0.0088; printed_expected=True; printed_4dp=True; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=True; PASS_complete=True
- **qwen3.5-9b C s3**: ran_ok=True; portfolio_var=(parsed from source); expected=0.0103; printed_expected=True; printed_4dp=True; comment_mentions_correlation=True; has_weight_sum_check=True; has_negative_check=True; PASS_correct=True; PASS_complete=True
- **qwen3.5-9b D s1**: words=94; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **qwen3.5-9b D s2**: words=83; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **qwen3.5-9b D s3**: words=96; lang=en; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **qwen3.5-9b E s1**: words=94; lang=fr; PASS_complete=True; note=Word count covers the whole answer, including the practical situation.
- **qwen3.5-9b E s2**: words=104; lang=fr; PASS_complete=False; note=Word count covers the whole answer, including the practical situation.
- **qwen3.5-9b E s3**: words=101; lang=fr; PASS_complete=False; note=Word count covers the whole answer, including the practical situation.
- **qwen3.5-9b F s1**: q1_17h35=True; q2_stays_in_book=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=True; PASS_complete=True
- **qwen3.5-9b F s2**: q1_17h35=True; q2_stays_in_book=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=True; PASS_complete=True
- **qwen3.5-9b F s3**: q1_17h35=True; q2_stays_in_book=True; q3_says_not_in_text=True; sentences=3; lang=fr; PASS_correct=True; PASS_complete=True
