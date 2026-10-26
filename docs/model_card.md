# Model card: basket inflation forecast

**Task.** Forecast the month-on-month change of a basket price index 1–3 months ahead.

**Input.** Monthly basket index built from official CPI divisions (`data/processed/cpi_divisions.csv`) and the user's spending shares.

**Methods compared.**

| Method | Rule |
|---|---|
| Naive | Next month's change = last month's change |
| Seasonal naive | Next month's change = change in the same month a year ago |
| 12-month mean | Next month's change = average monthly change over the last 12 months |

**Validation.** Walk-forward, one step ahead, over the last 12 months. For each test month, only earlier data is used. No random train/test split. Metrics: MAE and RMSE in percentage points of monthly change.

**Selection rule.** Lowest MAE wins. A more complex method is added to the comparison only if it can be tested the same way, and is used only if it beats the baselines.

**Results (official basket, Oct 2025 – Sep 2026).**

| Method | MAE, p.p. | RMSE, p.p. |
|---|---|---|
| 12-month mean | 0.196 | 0.266 |
| Naive | 0.263 | 0.361 |
| Seasonal naive | 0.330 | 0.495 |

**Uncertainty.** 95% band = ±1.96 · RMSE · √h around the cumulative forecast.

**Known weaknesses.**

- Only 26 months of data: seasonal methods see just one previous year.
- Administrative price changes (utility tariffs, e.g. June 2026 housing +7.8% m/m) are not predictable from past prices and produce the largest errors.
- Not suitable for horizons beyond a few months.

**Intended use.** Showing a person how their basket may move in the near term, with visible uncertainty. Not for financial decisions.
