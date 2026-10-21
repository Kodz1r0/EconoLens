"""Print the main results: personal inflation for example baskets, gap vs official CPI,
forecast backtest. Results go to reports/results.md as well.

Run:  python scripts/run_analysis.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from econolens.data import load_official_weights, load_series  # noqa: E402
from econolens.forecast import forecast  # noqa: E402
from econolens.index import basket_index, gap_decomposition, personal_inflation  # noqa: E402

# Illustrative baskets (shares in %). These are examples, not survey data.
BASKETS = {
    "student": dict(food=28, clothing=8, housing=8, furnishings=2, health=2, transport=14,
                    communication=7, recreation=6, education=15, restaurants=6, misc=4),
    "family_with_children": dict(food=44, alcohol=1, clothing=9, housing=13, furnishings=5, health=5,
                                 transport=8, communication=3, recreation=2, education=6, restaurants=1, misc=3),
    "pensioner": dict(food=48, alcohol=1, clothing=4, housing=18, furnishings=4, health=14,
                      transport=3, communication=3, recreation=1, misc=4),
}


def main() -> None:
    series = load_series()
    official = load_official_weights()
    last = series.index[-1]
    lines = [f"# Results ({series.index[0]} .. {last})", ""]

    pi_off = personal_inflation(series, official)
    lines += ["## 12-month inflation by basket", "", "| Basket | Inflation | Gap vs official, p.p. | Largest gap driver |", "|---|---|---|---|"]
    lines.append(f"| official (estimated weights) | {pi_off:.2%} | - | - |")
    for name, w in BASKETS.items():
        pi = personal_inflation(series, w)
        gap = gap_decomposition(series, w, official)
        lines.append(f"| {name} | {pi:.2%} | {(pi - pi_off) * 100:+.2f} | {gap.index[0]} ({gap.iloc[0] * 100:+.2f}) |")

    fc = forecast(basket_index(series, official))
    lines += ["", "## Forecast backtest (official basket, 1 month ahead, last 12 months)", "",
              "| Method | How it works | MAE, p.p. | RMSE, p.p. |", "|---|---|---|---|",
              *[f"| {r.method} | {r.description} | {r.mae_pp:.3f} | {r.rmse_pp:.3f} |" for r in fc["backtest"].itertuples()], "",
              f"Chosen method: **{fc['method']}**. Next 3 months: "
              f"{fc['path'][-1]['cum_change']:+.2%} (95% band {fc['path'][-1]['low']:+.2%} .. {fc['path'][-1]['high']:+.2%})."]

    text = "\n".join(lines) + "\n"
    print(text)
    out = ROOT / "reports" / "results.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    pd.set_option("display.width", 120)
    main()
