"""Short-term forecasts of a basket's monthly inflation, with honest backtesting.

All methods forecast the month-on-month change of the basket index. They are compared
with walk-forward validation: for each of the last `n_test` months, a method only sees
data before that month. A more complex method is chosen only if it beats the simpler
ones on mean absolute error (MAE).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd


@dataclass
class Method:
    name: str
    description: str
    min_history: int
    predict: Callable[[np.ndarray], float]  # history of monthly changes -> next month


METHODS = [
    Method("naive", "next month = last month", 1, lambda h: h[-1]),
    Method("seasonal_naive", "same month one year ago", 12, lambda h: h[-12]),
    Method("mean_12m", "average monthly change over the last 12 months", 12, lambda h: float(np.mean(h[-12:]))),
]


def monthly_changes(index: pd.Series) -> pd.Series:
    """Month-on-month change of an index (0.005 = +0.5%)."""
    return (index / index.shift(1) - 1).dropna()


def backtest(index: pd.Series, n_test: int = 12, methods=METHODS) -> pd.DataFrame:
    """One-step-ahead walk-forward errors for each method, in percentage points."""
    m = monthly_changes(index).to_numpy()
    n = len(m)
    rows = []
    for meth in methods:
        start = n - n_test
        if start < meth.min_history:
            continue
        errors = np.array([m[o] - meth.predict(m[:o]) for o in range(start, n)])
        rows.append({
            "method": meth.name,
            "description": meth.description,
            "mae_pp": float(np.mean(np.abs(errors)) * 100),
            "rmse_pp": float(np.sqrt(np.mean(errors**2)) * 100),
        })
    return pd.DataFrame(rows).sort_values("mae_pp").reset_index(drop=True)


def forecast(index: pd.Series, horizon: int = 3, n_test: int = 12, methods=METHODS) -> dict:
    """Forecast the basket index `horizon` months ahead with the best backtested method.

    Returns the chosen method, the backtest table and a list of dicts with the cumulative
    change from the last observed month and a 95% band based on backtest RMSE.
    """
    table = backtest(index, n_test, methods)
    best_name = table.iloc[0]["method"]
    best = next(x for x in methods if x.name == best_name)
    rmse = table.iloc[0]["rmse_pp"] / 100

    history = list(monthly_changes(index).to_numpy())
    level = float(index.iloc[-1])
    path, cum = [], 1.0
    for h in range(1, horizon + 1):
        r = best.predict(np.array(history))
        history.append(r)  # recursive forecast
        cum *= 1 + r
        band = 1.96 * rmse * math.sqrt(h)
        path.append({
            "step": h,
            "level": level * cum,
            "cum_change": cum - 1,
            "low": cum - 1 - band,
            "high": cum - 1 + band,
        })
    return {"method": best_name, "backtest": table, "path": path}
