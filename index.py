"""Personal price index, personal inflation and purchasing-power calculations.

Weights are expenditure SHARES (they sum to 1). Because of that, a basket index is
the share-weighted average of price RELATIVES, not of price levels:

    personal inflation (12m) = sum_i w_i * (I_i,t / I_i,t-12) - 1
    PPI_t                    = 100 * sum_i w_i * (I_i,t / I_i,0)

The formula sum(w*p_t) / sum(w*p_0) is only correct when w are quantities.
"""
from __future__ import annotations

from typing import Mapping

import pandas as pd


def normalize_weights(weights: Mapping[str, float] | pd.Series, columns) -> pd.Series:
    """Return shares that sum to 1, aligned to `columns`. Missing categories get 0."""
    w = pd.Series(weights, dtype=float).reindex(columns).fillna(0.0)
    if (w < 0).any():
        raise ValueError("Weights cannot be negative")
    total = w.sum()
    if total <= 0:
        raise ValueError("Weights must sum to a positive number")
    return w / total


def category_change(series: pd.DataFrame, month: str, lag: int = 12) -> pd.Series:
    """Price change of each division between `month - lag` and `month` (0.063 = +6.3%)."""
    t = series.index.get_loc(month)
    if t - lag < 0:
        raise ValueError(f"Need {lag} months of history before {month}")
    return series.iloc[t] / series.iloc[t - lag] - 1


def personal_inflation(series: pd.DataFrame, weights, month: str | None = None, lag: int = 12) -> float:
    """Inflation of a personal basket over `lag` months ending in `month` (default: last month)."""
    month = month or series.index[-1]
    w = normalize_weights(weights, series.columns)
    return float((w * category_change(series, month, lag)).sum())


def contributions(series: pd.DataFrame, weights, month: str | None = None, lag: int = 12) -> pd.Series:
    """Contribution of each division to personal inflation. Sums exactly to personal_inflation()."""
    month = month or series.index[-1]
    w = normalize_weights(weights, series.columns)
    return (w * category_change(series, month, lag)).sort_values(ascending=False)


def gap_decomposition(series: pd.DataFrame, weights, reference_weights, month: str | None = None, lag: int = 12) -> pd.Series:
    """Explain the gap between personal and reference (official) inflation by division.

    gap_i = (w_i - w_ref_i) * (r_i - pi_ref). The terms sum exactly to pi_personal - pi_ref,
    because the weight differences sum to zero.
    """
    month = month or series.index[-1]
    w = normalize_weights(weights, series.columns)
    w_ref = normalize_weights(reference_weights, series.columns)
    r = category_change(series, month, lag)
    pi_ref = float((w_ref * r).sum())
    gap = (w - w_ref) * (r - pi_ref)
    return gap.reindex(gap.abs().sort_values(ascending=False).index)


def basket_index(series: pd.DataFrame, weights) -> pd.Series:
    """Fixed-weight (Laspeyres-type) index of the basket, first month = 100."""
    w = normalize_weights(weights, series.columns)
    relatives = series / series.iloc[0]
    return 100 * (relatives * w).sum(axis=1)


def real_wage_growth(wage_now: float, wage_before: float, inflation: float) -> float:
    """Real growth of a wage: (1 + nominal growth) / (1 + inflation) - 1."""
    if wage_before <= 0:
        raise ValueError("Previous wage must be positive")
    return (wage_now / wage_before) / (1 + inflation) - 1


def wage_needed(wage_before: float, inflation: float) -> float:
    """Wage needed today to buy what `wage_before` bought before."""
    return wage_before * (1 + inflation)


def scenario_impact(weights, shocks: Mapping[str, float], columns) -> float:
    """One-off change in basket cost for given price shocks by division (0.10 = +10%)."""
    w = normalize_weights(weights, columns)
    s = pd.Series(shocks, dtype=float).reindex(columns).fillna(0.0)
    return float((w * s).sum())
