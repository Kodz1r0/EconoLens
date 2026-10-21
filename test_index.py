import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from econolens.data import load_official_weights, load_series  # noqa: E402
from econolens.index import (  # noqa: E402
    basket_index,
    contributions,
    gap_decomposition,
    normalize_weights,
    personal_inflation,
    real_wage_growth,
    scenario_impact,
    wage_needed,
)


@pytest.fixture
def toy():
    # Two categories, 13 months: A rises 10% over the year, B is flat.
    months = [f"2025-{m:02d}" for m in range(1, 13)] + ["2026-01"]
    a = [100 * 1.1 ** (i / 12) for i in range(13)]
    return pd.DataFrame({"A": a, "B": [100.0] * 13}, index=months)


def test_hand_calculated_example(toy):
    # 70% in A (+10%), 30% in B (0%) -> 7%
    assert personal_inflation(toy, {"A": 70, "B": 30}) == pytest.approx(0.07)


def test_weights_are_normalized(toy):
    assert personal_inflation(toy, {"A": 7, "B": 3}) == pytest.approx(personal_inflation(toy, {"A": 0.7, "B": 0.3}))
    assert normalize_weights({"A": 1}, ["A", "B"]).tolist() == [1.0, 0.0]


def test_negative_or_empty_weights_rejected(toy):
    with pytest.raises(ValueError):
        normalize_weights({"A": -1, "B": 2}, toy.columns)
    with pytest.raises(ValueError):
        normalize_weights({"A": 0, "B": 0}, toy.columns)


def test_contributions_sum_to_inflation(toy):
    w = {"A": 40, "B": 60}
    assert contributions(toy, w).sum() == pytest.approx(personal_inflation(toy, w))


def test_gap_decomposition_sums_to_gap():
    s = load_series()
    official = load_official_weights()
    w = {"food": 50, "housing": 20, "health": 15, "transport": 15}
    gap = gap_decomposition(s, w, official)
    assert gap.sum() == pytest.approx(personal_inflation(s, w) - personal_inflation(s, official))


def test_basket_index_starts_at_100(toy):
    idx = basket_index(toy, {"A": 1, "B": 1})
    assert idx.iloc[0] == pytest.approx(100)
    assert idx.iloc[-1] == pytest.approx(105)


def test_official_basket_matches_published_headline():
    # Published headline CPI, September 2026 vs September 2025: 106.4 (rounded to 0.1)
    s = load_series()
    assert personal_inflation(s, load_official_weights(), "2026-09") == pytest.approx(0.064, abs=0.0015)


def test_division_changes_match_release():
    # Release for September 2026, column "to September 2025"
    s = load_series()
    r = s.loc["2026-09"] / s.loc["2025-09"] - 1
    assert r["food"] == pytest.approx(0.063, abs=0.0015)
    assert r["housing"] == pytest.approx(0.118, abs=0.0015)
    assert r["transport"] == pytest.approx(0.072, abs=0.0015)


def test_wages():
    assert real_wage_growth(110, 100, 0.10) == pytest.approx(0.0)
    assert wage_needed(100, 0.064) == pytest.approx(106.4)


def test_scenario(toy):
    assert scenario_impact({"A": 50, "B": 50}, {"A": 0.10}, toy.columns) == pytest.approx(0.05)
