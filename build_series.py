"""Rebuild the monthly CPI series by division from the raw press-release table.

Input:  data/raw/stat_uz_cpi_releases.csv   (values as printed in stat.uz releases)
        data/raw/stat_uz_contributions.csv  (contributions to headline CPI, p.p.)
Output: data/processed/cpi_divisions.csv              (index levels, Dec 2024 = 100)
        data/processed/official_weights_estimated.csv (estimated basket weights)

Method (levels L, Dec 2024 = 100):
  * Aug-Dec 2025: L = "to December of previous year" value from that month's release.
  * 2026:         L = L(Dec 2025) * "to December 2025" / 100.
  * Jan-Jul 2025 and Aug-Nov 2024: L = L(same month next year) / "to same month last year" * 100.
Checks: the month-on-month chain must agree with year-to-date values, and Aug/Sep 2025
computed in two ways must agree, within rounding.

Run:  python scripts/build_series.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from econolens.data import DIVISION_IDS, RAW_CONTRIBUTIONS, RAW_RELEASES, SERIES, WEIGHTS  # noqa: E402

TOLERANCE = 0.16  # p.p.; releases round to 0.1


def prev_month(m: str, k: int = 1) -> str:
    y, mo = int(m[:4]), int(m[5:]) - 1 - k
    y += mo // 12
    return f"{y}-{mo % 12 + 1:02d}"


def main() -> None:
    raw = pd.read_csv(RAW_RELEASES, dtype={"release_month": str})
    raw = raw[raw["division"].isin(DIVISION_IDS)]
    mom = raw.pivot(index="release_month", columns="division", values="mom")[DIVISION_IDS]
    ytd = raw.pivot(index="release_month", columns="division", values="ytd")[DIVISION_IDS]
    yoy = raw.pivot(index="release_month", columns="division", values="yoy")[DIVISION_IDS]
    releases = list(ytd.index)

    # Check 1: ytd(t) ~= ytd(t-1) * mom(t) within a calendar year
    for a, b in zip(releases, releases[1:]):
        if b.endswith("-01"):
            continue
        diff = (ytd.loc[a] * mom.loc[b] / 100 - ytd.loc[b]).abs()
        if (diff > TOLERANCE).any():
            raise SystemExit(f"Inconsistent release {b}: {diff[diff > TOLERANCE].to_dict()}")

    levels: dict[str, pd.Series] = {"2024-12": pd.Series(100.0, index=DIVISION_IDS)}
    for m in releases:
        if m.startswith("2025"):
            levels[m] = ytd.loc[m]
    for m in releases:
        if m.startswith("2026"):
            levels[m] = levels["2025-12"] * ytd.loc[m] / 100
    for mo in range(1, 13):
        m25, m26 = f"2025-{mo:02d}", f"2026-{mo:02d}"
        if m26 in releases:
            back = levels[m26] / yoy.loc[m26] * 100
            if m25 in levels:  # Check 2: two routes to the same month agree
                gap = (back - levels[m25]).abs().max()
                if gap > 2 * TOLERANCE:
                    raise SystemExit(f"{m25}: two estimates differ by {gap:.2f} p.p.")
            else:
                levels[m25] = back
    for m in releases:
        if m.startswith("2025"):
            m24 = prev_month(m, 12)
            if m24 not in levels:
                levels[m24] = levels[m] / yoy.loc[m] * 100

    series = pd.DataFrame(levels).T.sort_index()
    series.index.name = "month"
    months = list(series.index)
    for a, b in zip(months, months[1:]):
        if prev_month(b) != a:
            raise SystemExit(f"Gap in series between {a} and {b}")
    SERIES.parent.mkdir(parents=True, exist_ok=True)
    series.to_csv(SERIES, float_format="%.3f")
    print(f"Series: {len(series)} months, {months[0]} .. {months[-1]} -> {SERIES.relative_to(SERIES.parents[2])}")

    # Estimated official weights: weight = contribution / (division change since December)
    contrib = pd.read_csv(RAW_CONTRIBUTIONS, dtype={"release_month": str})
    c = contrib[contrib["release_month"] == "2026-09"].set_index("division")["contribution_pp"].reindex(DIVISION_IDS)
    w = c / (ytd.loc["2026-09"] - 100)
    w = (w / w.sum() * 100).round(1)
    w.iloc[0] = round(w.iloc[0] + 100 - w.sum(), 1)
    pd.DataFrame({"division": DIVISION_IDS, "weight_pct": w.values}).to_csv(WEIGHTS, index=False)
    print("Estimated 2026 weights, %:", {k: float(v) for k, v in zip(DIVISION_IDS, w.values)})


if __name__ == "__main__":
    main()
