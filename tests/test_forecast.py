import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from econolens.forecast import backtest, forecast, monthly_changes  # noqa: E402


def make_index(changes):
    return pd.Series(100 * np.cumprod([1.0] + [1 + c for c in changes]))


def test_constant_growth_is_forecast_exactly():
    idx = make_index([0.005] * 30)
    res = forecast(idx, horizon=3)
    assert res["backtest"]["mae_pp"].min() == pytest.approx(0, abs=1e-9)
    assert res["path"][-1]["cum_change"] == pytest.approx(1.005**3 - 1)


def test_seasonal_pattern_prefers_seasonal_naive():
    pattern = [0.01, 0.0, -0.005, 0.002] * 3
    idx = make_index(pattern * 3)
    assert backtest(idx).iloc[0]["method"] == "seasonal_naive"


def test_backtest_uses_only_past_data():
    # A jump in the last month cannot be predicted by any method
    idx = make_index([0.005] * 29 + [0.05])
    assert backtest(idx)["mae_pp"].min() > 0


def test_monthly_changes_length():
    idx = make_index([0.01] * 5)
    assert len(monthly_changes(idx)) == 5
