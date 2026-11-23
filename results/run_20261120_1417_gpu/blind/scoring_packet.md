# Blind scoring packet

Score each answer on the sheet. Do not open key.json until you have finished.

## Prompt A: Performance calculation (Sharpe ratio)

**Prompt:**

```text
Write a Python function that calculates the Sharpe ratio given three inputs:
- a list of daily returns (as floats)
- the risk-free rate (annual, as a float, e.g. 0.04)
- trading days per year (default 252)

Handle edge cases (empty list, zero volatility).
Include type hints, a clear docstring, and 2–3 simple unit tests.
```

### A1

**Python implementation**

```python
import math
from typing import List


def sharpe_ratio(
    daily_returns: List[float],
    risk_free_rate_annual: float,
    trading_days_per_year: int = 252,
) -> float:
    """
    Calculate the annual Sharpe ratio from a list of daily returns.

    The Sharpe ratio is computed as:
        Sharpe = ((mean daily excess return) / std daily returns) * sqrt(trading_days_per_year)

    Where:
        * daily_returns – list of daily returns (float)
        * risk_free_rate_annual – annual risk‑free rate (e.g., 0.04)
        * trading_days_per_year – number of trading days in a year (default 252)

    Parameters
    ----------
    daily_returns : List[float]
        Daily returns of the investment (float). Must contain at least one element.
    risk_free_rate_annual : float
        Annual risk‑free rate expressed as a decimal (e.g., 0.04 for 4%).
    trading_days_per_year : int, optional
        Number of trading days in a year (default is 252).

    Returns
    -------
    float
        The Sharpe ratio (annualized).

    Raises
    ------
    ValueError
        If ``daily_returns`` is empty or if the standard deviation is zero.
    """
    if not daily_returns:
        raise ValueError("daily_returns list cannot be empty")

    # Mean of daily returns
    mean_daily = sum(daily_returns) / len(daily_returns)

    # Standard deviation of daily returns (sample)
    if len(daily_returns) < 2:
        raise ValueError("At least two daily returns are required to compute std")
    std_daily = math.sqrt(sum((x - mean_daily) ** 2 for x in daily_returns) / (len(daily_returns) - 1))

    # Convert risk‑free rate to a daily rate
    daily_rf = risk_free_rate_annual / trading_days_per_year

    # Excess return per day
    excess_daily = mean_daily - daily_rf

    # Annual Sharpe ratio
    sharpe = (excess_daily / std_daily) * math.sqrt(trading_days_per_year)

    return sharpe
```

**Simple unit tests**

```python
import math
from your_module import sharpe_ratio  # replace `your_module` with the actual filename

def test_sharpe_ratio_basic():
    # Example: returns = [-0.01, 0.02, 0.00], rf = 0.04, 250 trading days
    returns = [-0.01, 0.02, 0.00]
    # Manual calculation:
    # mean = 0.01, daily_rf = 0.04/250 = 0.00016, excess = 0.0098333
    # std ≈ 0.0201, Sharpe = (0.0098333/0.0201)*sqrt(250) ≈ 0.49
    assert abs(sharpe_ratio(returns, 0.04, 250)) < 0.01

def test_sharpe_ratio_empty_list():
    try:
        sharpe_ratio([], 0.04, 252)
    except ValueError as e:
        assert "cannot be empty" in str(e)

def test_sharpe_ratio_zero_volatility():
    # All daily returns are zero → std = 0
    zero_returns = [0.0, 0.0, 0.0]
    try:
        sharpe_ratio(zero_returns, 0.02, 252)
    except ValueError as e:
        assert "Zero volatility" in str(e)
```

*The tests above cover the main edge cases and a simple example.*

---

### A2

Certainly! Below is a Python function that calculates the Sharpe ratio given the specified inputs, along with type hints, a clear docstring, and simple unit tests.

```python
from typing import List
import numpy as np

def calculate_sharpe_ratio(daily_returns: List[float], risk_free_rate: float, trading_days_per_year: int = 252) -> float:
    """
    Calculate the Sharpe ratio given a list of daily returns, the risk-free rate, and the number of trading days per year.

    Parameters:
    daily_returns (List[float]): A list of daily returns.
    risk_free_rate (float): The annual risk-free rate.
    trading_days_per_year (int, optional): The number of trading days per year. Default is 252.

    Returns:
    float: The Sharpe ratio. Returns None if the input list is empty or if the volatility is zero.

    Raises:
    ValueError: If the input list is empty or if the volatility is zero.
    """
    if not daily_returns:
        raise ValueError("The list of daily returns cannot be empty.")
    
    # Calculate the average daily return and the standard deviation of daily returns
    avg_daily_return = np.mean(daily_returns)
    std_daily_return = np.std(daily_returns)
    
    # Annualize the standard deviation of daily returns
    annualized_std_dev = std_daily_return * np.sqrt(trading_days_per_year)
    
    if annualized_std_dev == 0:
        raise ValueError("The volatility is zero, Sharpe ratio is undefined.")
    
    # Calculate the Sharpe ratio
    sharpe_ratio = (avg_daily_return - (risk_free_rate / trading_days_per_year)) / annualized_std_dev
    
    return sharpe_ratio

# Unit tests
def test_calculate_sharpe_ratio():
    # Test case 1: Normal case
    daily_returns = [0.001, 0.002, -0.001, 0.003, 0.002]
    risk_free_rate = 0.04
    expected_sharpe_ratio = 0.002
    assert np.isclose(calculate_sharpe_ratio(daily_returns, risk_free_rate), expected_sharpe_ratio, atol=1e-5)
    
    # Test case 2: Zero volatility
    daily_returns = [0.001, 0.001, 0.001, 0.001, 0.001]
    risk_free_rate = 0.04
    try:
        calculate_sharpe_ratio(daily_returns, risk_free_rate)
        assert False, "Expected ValueError for zero volatility"
    except ValueError:
        pass
    
    # Test case 3: Empty list
    try:
        calculate_sharpe_ratio([], risk_free_rate)
        assert False, "Expected ValueError for empty list"
    except ValueError:
        pass

# Run the unit tests
test_calculate_sharpe_ratio()
print("All tests passed.")
```

Explanation:
1. The function `calculate_sharpe_ratio` takes three parameters: a list of daily returns, the risk-free rate, and the number of trading days per year (default is 252).
2. It checks if the list of daily returns is empty and raises a `ValueError` if it is.
3. It calculates the average daily return and the standard deviation of daily returns.
4. It annualizes the standard deviation of daily returns.
5. If the annualized standard deviation is zero, it raises a `ValueError` because the Sharpe ratio is undefined in this case.
6. It calculates and returns the Sharpe ratio.
7. The function includes simple unit tests to verify its correctness.

You can run the provided unit tests to ensure the function works as expected. If all tests pass, it will print "All tests passed."

---

### A3

```python
from typing import List, Union

def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.04,
    trading_days_per_year: int = 252
) -> float:
    """
    Calculate the annualized Sharpe ratio given daily returns.

    The Sharpe ratio measures the performance of an investment compared to a risk-free asset, 
    after adjusting for its risk. It is calculated as the excess return per unit of deviation 
    in the portfolio.

    Formula:
        Sharpe Ratio = (Portfolio Return - Risk Free Rate) / Standard Deviation
        Annualized = ((1 + Daily_Returns_Product)^Trading_Days - 1) ... 
        However, standard approximation for small returns:
        Annualized Return ≈ Daily Mean * Trading Days
        Annualized Volatility ≈ Daily StdDev * sqrt(Trading Days)

    Parameters
    ----------
    returns : List[float]
        A list of daily returns as decimals (e.g., 0.01 for 1%).
    risk_free_rate : float
        The annual risk-free rate as a decimal (default: 0.04).
    trading_days_per_year : int
        Number of trading days in a year (default: 252).

    Returns
    -------
    float
        The annualized Sharpe ratio.

    Raises
    ------
    ValueError
        If the returns list is empty or if volatility is zero (division by zero).

    Examples
    --------
    >>> calculate_sharpe_ratio([0.01, -0.02, 0.03], risk_free_rate=0.02)
    1.4142135623730951
    """
    
    # Edge case: Empty list
    if not returns:
        raise ValueError("Returns list cannot be empty.")

    n = len(returns)
    
    # Calculate mean daily return
    mean_daily_return = sum(returns) / n
    
    # Calculate standard deviation of daily returns (population std dev)
    variance = sum((x - mean_daily_return) ** 2 for x in returns) / n
    daily_std_dev = variance ** 0.5

    # Edge case: Zero volatility
    if daily_std_dev == 0:
        raise ValueError("Volatility is zero; Sharpe ratio cannot be calculated.")

    # Annualize the metrics
    # Approximation: Mean scales linearly, StdDev scales with sqrt(time)
    annualized_return = mean_daily_return * trading_days_per_year
    annualized_volatility = daily_std_dev * (trading_days_per_year ** 0.5)

    # Calculate Sharpe Ratio
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility

    return sharpe_ratio


# --- Unit Tests ---

def test_calculate_sharpe_ratio():
    # Test 1: Standard case with positive excess return
    daily_returns = [0.01, -0.01, 0.02]
    rf_rate = 0.04
    expected_positive = calculate_sharpe_ratio(daily_returns, rf_rate)
    assert isinstance(expected_positive, float), "Result should be a float."

    # Test 2: Zero volatility edge case (should raise ValueError)
    zero_vol_returns = [0.01, 0.01, 0.01]
    try:
        calculate_sharpe_ratio(zero_vol_returns, rf_rate=0.04)
        assert False, "Should have raised ValueError for zero volatility."
    except ValueError as e:
        assert "Volatility is zero" in str(e), f"Wrong error message: {e}"

    # Test 3: Negative excess return (result should be negative)
    negative_returns = [-0.01, -0.02, -0.03]
    result_negative = calculate_sharpe_ratio(negative_returns, rf_rate=0.04)
    assert result_negative < 0, "Sharpe ratio should be negative for negative excess return."

    # Test 4: Empty list edge case (should raise ValueError)
    empty_returns = []
    try:
        calculate_sharpe_ratio(empty_returns, rf_rate=0.04)
        assert False, "Should have raised ValueError for empty list."
    except ValueError as e:
        assert "empty" in str(e).lower(), f"Wrong error message: {e}"

if __name__ == "__main__":
    test_calculate_sharpe_ratio()
    print("All unit tests passed.")
```

---

## Prompt B: Bug fixing (cumulative returns)

**Prompt:**

```text
This function is meant to compute cumulative returns from a list of daily simple returns, but it is wrong. Fix it and briefly explain the bug.

def cumulative_returns(daily_returns):
    cum = 1.0
    results = []
    for r in daily_returns:
        cum = cum + r
        results.append(cum - 1)
    return results
```

### B1

The bug in the provided function is that it incorrectly computes the cumulative returns by adding the daily returns directly to the cumulative product instead of multiplying them. The correct approach is to multiply the cumulative product by (1 + daily return) for each day. Here is the corrected version of the function:

```python
def cumulative_returns(daily_returns):
    cum = 1.0
    results = []
    for r in daily_returns:
        cum *= (1 + r)
        results.append(cum)
    return results
```

Explanation of the bug:
- The original function incorrectly adds the daily return `r` to the cumulative product `cum` instead of multiplying it by `(1 + r)`. This results in an incorrect cumulative return calculation.
- The corrected function multiplies the cumulative product by `(1 + r)` for each daily return, which correctly computes the cumulative returns. The `results` list stores the cumulative returns at each step, starting from an initial value of 1.0 (representing 100% of the initial value).

---

### B2

The bug is that the cumulative return is computed by adding the daily returns instead of multiplying them. Cumulative return is the product of (1 + daily return), not the sum.

**Fix:**
```python
def cumulative_returns(daily_returns):
    cum = 1.0          # start with 1 (no change)
    results = []
    for r in daily_returns:
        cum *= (1 + r)   # multiply by (1 + daily return)
        results.append(cum - 1)
    return results
```

**Explanation:**  
The original code added each daily return to `cum` (`cum = cum + r`) which yields the sum of returns, not the compound growth. Multiplying `cum` by `(1 + r)` correctly computes the cumulative product, and subtracting 1 converts it to the total return (e.g., 0.02 means a 2 % cumulative gain).

---

### B3

### Fixed Code

```python
def cumulative_returns(daily_returns):
    cum = 1.0
    results = []
    for r in daily_returns:
        # Corrected line: multiply instead of add
        cum = cum * (1 + r)
        results.append(cum - 1)
    return results
```

### Explanation of the Bug

The original function incorrectly **added** the daily return to the cumulative value (`cum = cum + r`).

In finance, returns are compounded. If you have a portfolio worth $100$ and it gains $10\%$, it becomes $110$. If it then loses $10\%$, it drops to $99$, not back to $100$. The error arises because addition assumes the percentage applies to the original base every time, rather than the current growing total.

**Correct Logic:**
To update the cumulative wealth factor, you must multiply the previous factor by $(1 + \text{daily\_return})$.
*   **Wrong:** $Cum_{new} = Cum_{old} + r$ (Linear accumulation)
*   **Right:** $Cum_{new} = Cum_{old} \times (1 + r)$ (Geometric/Compound accumulation)

---

## Prompt C: Multi-step script (portfolio volatility)

**Prompt:**

```text
Write a complete Python script (standard library only) that:
1. Defines a small portfolio as a list of dicts: [{"ticker": "AAPL", "weight": 0.4, "daily_vol": 0.015}, ...]
2. Calculates the portfolio’s approximate daily volatility assuming zero correlation between assets
3. Prints the result rounded to 4 decimal places
4. Includes basic checks (weights sum roughly to 1, no negative weights)

Add a short comment explaining the zero-correlation assumption.
```

### C1

```python
# Import the standard library module for square root calculation
import math

# Define a small portfolio as a list of dictionaries
# Each dictionary contains the asset ticker, its weight in the portfolio,
# and its estimated daily volatility
portfolio = [
    {"ticker": "AAPL", "weight": 0.4, "daily_vol": 0.015},
    {"ticker": "MSFT", "weight": 0.6, "daily_vol": 0.012}
]

# 1. Check that all weights are non‑negative
all_weights_non_negative = all(p["weight"] >= 0 for p in portfolio)
if not all_weights_non_negative:
    raise ValueError("Negative weights are not allowed")

# 2. Check that the weights roughly sum to 1 (within a small tolerance)
total_weight = sum(p["weight"] for p in portfolio)
if not math.isclose(total_weight, 1.0, rel_tol=1e-3):
    raise ValueError(f"Weights do not sum to 1 (got {total_weight})")

# 3. Calculate portfolio daily volatility assuming zero correlation between assets
#    Under zero correlation, the covariance terms are zero.
#    Portfolio variance = Σ (weight_i^2 * daily_vol_i^2)
portfolio_volatility = math.sqrt(
    sum((p["weight"] ** 2) * (p["daily_vol"] ** 2) for p in portfolio)
)

# 4. Print the result rounded to 4 decimal places
print(f"Portfolio daily volatility: {portfolio_volatility:.4f}")

# Comment about the zero-correlation assumption
# Zero correlation means that the volatility of any two assets can be treated as independent,
# so the total volatility of the portfolio is simply the square root of the sum of each asset's
# contribution to variance (no covariance terms to add).
```

---

### C2

```python
import math

def validate_and_calculate(portfolio):
    """
    Validates the portfolio data and calculates daily volatility assuming zero correlation.
    
    Args:
        portfolio (list[dict]): List of asset dicts with 'ticker', 'weight', and 'daily_vol'.
        
    Returns:
        float: Approximate daily portfolio volatility.
    """
    if not portfolio:
        raise ValueError("Portfolio cannot be empty.")

    total_weight = 0.0
    weighted_variances = []

    for item in portfolio:
        ticker = item.get("ticker")
        weight = item.get("weight")
        daily_vol = item.get("daily_vol")

        # Basic validation checks
        if not all([ticker, weight is not None, daily_vol is not None]):
            raise ValueError(f"Missing data for asset: {item}")
        
        if weight < 0:
            raise ValueError(f"Negative weight found for {ticker}: {weight}")
        if daily_vol < 0:
            raise ValueError(f"Negative volatility found for {ticker}: {daily_vol}")
            
        total_weight += weight
        # Variance is the square of volatility
        weighted_variances.append(weight * (daily_vol ** 2))

    # Check if weights sum roughly to 1 (allowing small floating point errors)
    if not math.isclose(total_weight, 1.0, abs_tol=1e-4):
        raise ValueError(f"Weights do not sum to 1: {total_weight}")

    # Calculate portfolio variance assuming zero correlation
    # Formula: Var(P) = sum(w_i^2 * sigma_i^2) when correlations are 0
    portfolio_variance = sum(weighted_variances)
    
    return math.sqrt(portfolio_variance)

def main():
    # Define a small portfolio
    portfolio = [
        {"ticker": "AAPL", "weight": 0.4, "daily_vol": 0.015},
        {"ticker": "MSFT", "weight": 0.35, "daily_vol": 0.020},
        {"ticker": "GOOGL", "weight": 0.25, "daily_vol": 0.018}
    ]

    try:
        # Calculate volatility
        daily_volatility = validate_and_calculate(portfolio)
        
        # Print result rounded to 4 decimal places
        print(f"{daily_volatility:.4f}")
        
    except ValueError as e:
        print(f"Validation Error: {e}")

if __name__ == "__main__":
    main()
```

**Explanation of Zero-Correlation Assumption:**  
This script assumes that the returns of the different assets in the portfolio are uncorrelated (correlation coefficient = 0). Under this assumption, the covariance terms between any pair of assets vanish from the variance formula. The portfolio variance simplifies to the sum of each asset's weighted variance ($w_i^2 \sigma_i^2$), ignoring diversification benefits that would normally arise from negative or low positive correlations. In reality, stocks often move together, so actual volatility might differ significantly from this approximation.

---

### C3

```python
import math

# Define a small portfolio as a list of dicts
portfolio = [
    {"ticker": "AAPL", "weight": 0.4, "daily_vol": 0.015},
    {"ticker": "MSFT", "weight": 0.3, "daily_vol": 0.02},
    {"ticker": "GOOGL", "weight": 0.3, "daily_vol": 0.025}
]

# Function to calculate portfolio volatility
def calculate_portfolio_volatility(portfolio):
    # Check if weights sum roughly to 1
    total_weight = sum(asset["weight"] for asset in portfolio)
    if not math.isclose(total_weight, 1.0, abs_tol=0.01):
        raise ValueError("Weights do not sum to 1. Please check the portfolio weights.")
    
    # Check for negative weights
    if any(asset["weight"] < 0 for asset in portfolio):
        raise ValueError("Weights cannot be negative. Please check the portfolio weights.")
    
    # Zero-correlation assumption: When assets are uncorrelated, the portfolio volatility can be calculated as the square root of the weighted sum of individual volatilities squared.
    # This is because the covariance terms cancel out, leaving only the individual volatilities.
    portfolio_volatility = math.sqrt(sum(asset["weight"]**2 * asset["daily_vol"]**2 for asset in portfolio))
    
    return portfolio_volatility

# Calculate and print the portfolio's approximate daily volatility
try:
    volatility = calculate_portfolio_volatility(portfolio)
    print(f"Portfolio's approximate daily volatility: {volatility:.4f}")
except ValueError as e:
    print(e)
```

This script defines a small portfolio, calculates its approximate daily volatility under the assumption of zero correlation between assets, and includes basic checks for the weights. The zero-correlation assumption simplifies the calculation by allowing us to sum the weighted volatilities directly without considering covariances.

---

## Prompt D: Market vs limit order (English)

**Prompt:**

```text
Explain in under 100 words the difference between a market order and a limit order in equities. Then give one practical situation where a limit order is usually preferable.
```

### D1

A **market order** executes immediately at the best available current price, guaranteeing speed but not price. A **limit order** sets a specific maximum buy or minimum sell price; it only executes if the market reaches that level, guaranteeing price but not execution certainty.

**Practical Situation:** A limit order is preferable when trading volatile stocks nearing earnings reports. If you want to buy a stock but fear a sudden spike will make shares too expensive, setting a limit order ensures you pay no more than your target price, even if the market surges past it.

---

### D2

A market order executes immediately at the best available price; a limit order only executes when the price is at or better than the specified limit. Market orders risk price slippage; limit orders let you control price and fill only at your target. One practical situation: buying a stock you’re willing to pay at $50 per share, and you want to avoid overpaying by setting a limit order at that price.

---

### D3

A market order is executed immediately at the best available price, while a limit order sets a specific price at which the trade should be executed. A limit order is preferable when an investor wants to buy or sell a stock at a particular price or better, ensuring they don't pay more than the desired price, such as when the stock is volatile and prices fluctuate rapidly.

---

## Prompt E: Ordre au marché vs ordre à cours limité (French)

**Prompt:**

```text
Explique en moins de 100 mots la différence entre un ordre au marché et un ordre à cours limité en actions. Donne ensuite une situation concrète où l’ordre à cours limité est généralement préférable.
```

### E1

Un ordre au marché est exécuté immédiatement à la meilleure offre ou à la meilleure demande disponible, tandis qu’un ordre à cours limité est fixé à un prix spécifique et ne s’exécute que lorsque ce prix est atteint. Il est préférable pour les investisseurs souhaitant acheter ou vendre une quantité précise d'actions sans influencer le prix du marché, par exemple, lors de la mise en place d'un ordre à cours limité pour acheter des actions d'une entreprise à un prix prédéfini, garantissant ainsi une transaction sans avoir à payer plus que le prix souhaité en raison de fluctuations du marché.

---

### E2

Un ordre au marché s’exécute immédiatement au prix du marché, garantissant l’achat dès que le marché est prêt. Un ordre à cours limité fixe le prix maximum que vous êtes prêt à payer ou le minimum à accepter, évitant les cours supérieurs à votre cible. Un ordre au marché est rapide mais peut dépasser votre prix; un ordre à cours limité vous permet de contrôler le prix mais ne garantit pas l’exécution.

Par exemple, lors d’une forte volatilité d’une action, un investisseur qui souhaite entrer dans la position sans payer un prix trop élevé choisit un ordre à cours limité à 45 €. Cela évite de payer un prix plus élevé pendant une hausse soudaine.

---

### E3

Un ordre au marché exécute immédiatement l'achat ou vente au meilleur prix disponible, garantissant l'exécution mais pas le prix exact. Un ordre à cours limité spécifie un prix maximum d'achat ou minimum de vente ; il n'est exécuté que si ce seuil est atteint, protégeant ainsi votre capital mais risquant de ne jamais être rempli.

Situation préférable : Lors d'une forte volatilité haussière (ex: +5% en une minute), un investisseur souhaitant acheter une action sans payer le pic spéculatif utilisera un ordre limité pour éviter de se faire « prendre au piège » par des prix artificiellement élevés.

---

## Prompt F: Grounded answer from a given text (French)

**Prompt:**

```text
Texte :
« La plateforme Delta organise un fixing de clôture chaque jour de bourse. La phase d’accumulation des ordres commence à 17h30 et dure cinq minutes. Pendant cette phase, les ordres peuvent être saisis, modifiés ou annulés, mais aucune transaction n’a lieu. Le cours de clôture est le prix qui maximise le volume échangé. Si deux prix donnent le même volume, la plateforme retient celui qui laisse le plus petit déséquilibre entre achats et ventes. Les ordres au marché non exécutés au fixing sont annulés ; les ordres à cours limité non exécutés restent dans le carnet jusqu’à la fin de leur validité. »

En t’appuyant uniquement sur ce texte, réponds en trois phrases au plus :
1. À quelle heure se termine la phase d’accumulation ?
2. Que devient un ordre à cours limité non exécuté au fixing ?
3. Quels frais la plateforme facture-t-elle pour participer au fixing ?
Si le texte ne permet pas de répondre à une question, dis-le.
```

### F1

1. La phase d’accumulation se termine à 17h35.
2. Un ordre à cours limité non exécuté au fixing est annulé.
3. Le texte ne fournit pas d'informations sur les frais facturés par la plateforme pour participer au fixing.

---

### F2

La phase d’accumulation se termine à 18h00. Un ordre à cours limité non exécuté reste dans le carnet jusqu’à la fin de sa validité. Le texte ne mentionne aucun frais pour participer au fixing.

---

### F3

La phase d'accumulation se termine à 17h35 car elle commence à 17h30 et dure cinq minutes. Un ordre à cours limité non exécuté reste dans le carnet jusqu'à la fin de sa validité, tandis qu'un ordre au marché non exécuté est annulé. Le texte ne mentionne aucun frais facturés par la plateforme pour participer au fixing.

---
