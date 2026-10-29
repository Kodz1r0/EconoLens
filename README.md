# EconoLens Uzbekistan

**Personal inflation and purchasing power, built on official CPI data.**

Official inflation is an average. A household that spends half its budget on food, or a student who pays tuition, can face a very different number. EconoLens lets a person enter the shares of their spending, measures the inflation of *their* basket, compares it with the official CPI, shows what it means for their salary, and explains the result in Russian, Uzbek or English.

Live demo: https://abdijaliev.github.io/EconoLens/

> Status: MVP. Data through September 2026. The explanation layer is template-based for now; an LLM layer is planned (see [Roadmap](#roadmap)).

## Research question

How far does household-specific inflation in Uzbekistan differ from the official CPI, and which spending categories explain the gap?

## What the tool does

| Tab | What it shows |
|---|---|
| Basket | The user sets spending shares for 13 CPI divisions (or picks an example basket). |
| My inflation | 12-month inflation of the personal basket vs the official basket; contribution of each division; decomposition of the gap. |
| Salary | Real wage growth, the salary needed to keep last year's purchasing power, extra monthly cost of the same basket, 3-month outlook. Salary data never leaves the browser. |
| Forecast | 1–3 month forecast of the basket index with a 95% band, chosen by walk-forward backtest against simple baselines. |
| Scenarios | One-off shocks (som depreciation, utility tariffs, fuel, food) with editable pass-through assumptions. |
| Methodology & data | Formulas, data construction, CSV upload, limitations, sources. |

## Data

Source: monthly CPI press releases of the **Agency of Statistics under the President of the Republic of Uzbekistan** ([stat.uz](https://stat.uz)), 13 divisions of the national classification КИПЦ РУ 2018.

The Agency publishes CPI only as PDF releases, so the series is rebuilt from them:

| File | Content |
|---|---|
| `data/raw/stat_uz_cpi_releases.csv` | Values exactly as printed in 14 releases (Aug 2025 – Sep 2026): month-on-month, since December, year-on-year, with the source URL of every row. |
| `data/raw/stat_uz_contributions.csv` | Published contributions of each division to headline CPI (p.p.). |
| `data/processed/cpi_divisions.csv` | Monthly index levels by division, **Aug 2024 – Sep 2026, Dec 2024 = 100**. Built by `scripts/build_series.py`. |
| `data/processed/official_weights_estimated.csv` | Estimated official basket weights for 2026. |

See [`docs/data_dictionary.md`](docs/data_dictionary.md) for every column and the construction rules.

**Checks** (run automatically by the build script and tests):

- The month-on-month chain agrees with the "since December" values in every release (within 0.15 p.p., the rounding of the releases).
- August and September 2025, computed in two independent ways, agree within 0.12 p.p.
- Headline CPI recomputed with the estimated weights differs from the published figure by at most 0.1 p.p. (Sep 2026: 6.33% vs 6.4% published).

## Methodology

Weights `w_i` are **expenditure shares** (they sum to 1), so the basket index averages price *relatives*:

```
personal inflation (12m) = Σ w_i · (I_i,t / I_i,t−12) − 1
basket index PPI_t       = 100 · Σ w_i · (I_i,t / I_i,0)
contribution of i        = w_i · (I_i,t / I_i,t−12 − 1)          → sums to personal inflation
gap explained by i       = (w_i − w_ref,i) · (r_i − π_ref)        → sums to π_personal − π_official
real wage growth         = (1 + nominal growth) / (1 + π) − 1
```

The formula `Σ w·p_t / Σ w·p_0` is correct only when `w` are *quantities*, which is why it is not used here.

**Official weights.** The Agency does not publish division weights in its releases. They are estimated from published contributions: `weight_i = contribution_i / (division change since December)`, using the September 2026 release. Precision is about ±0.5 p.p. for large divisions.

**Forecast.** Methods: naive (last month), seasonal naive (same month last year), 12-month mean. Each is tested with walk-forward validation on the last 12 months (one step ahead, no random splits). The method with the lowest MAE is used; a complex model is never chosen unless it beats the baselines. The 95% band is ±1.96 · RMSE · √h.

## Results so far

From `python scripts/run_analysis.py` (12 months to September 2026, example baskets):

| Basket | Inflation | Gap vs official |
|---|---|---|
| Official (estimated weights) | 6.33% | – |
| Student (example) | 6.23% | −0.10 p.p. |
| Family with children (example) | 6.38% | +0.06 p.p. |
| Pensioner (example) | 6.62% | +0.29 p.p. (mostly housing & utilities, +11.8% y/y) |

Forecast backtest (official basket): 12-month mean MAE 0.196 p.p., naive 0.263 p.p., seasonal naive 0.330 p.p.

The example baskets are illustrations, not survey data. Real household baskets will come from the user survey.

## Limitations

- Category-level indices, not individual prices: inside a division prices move differently for different people.
- Fixed weights over the period; households that substitute away from expensive goods face slightly lower inflation.
- Release values are rounded to 0.1, so derived month-on-month changes can differ from published ones by about ±0.1 p.p.
- Official weights are estimates (see above).
- In January 2026 "Insurance and financial services" rose about 41% (motor insurance). The division's weight is small (~0.3%).
- Scenario pass-through coefficients are assumptions, not estimates.
- Forecasts are short-term statistical extrapolations, not predictions of policy or shocks.
- Not financial advice.

## Repository structure

```
data/raw/            values copied from stat.uz releases (+ source URLs)
data/processed/      series and weights built from raw data
src/econolens/       index, forecast and data-loading code
scripts/             build_series.py (rebuild data), run_analysis.py (results)
tests/               unit tests: hand-calculated examples and checks against releases
docs/index.html      the web app (served by GitHub Pages)
docs/                data dictionary, model card
reports/results.md   output of run_analysis.py
```

## Run locally

```bash
pip install -r requirements.txt
python scripts/build_series.py   # rebuild data/processed from data/raw
python scripts/run_analysis.py   # print results, write reports/results.md
pytest -q                        # run tests
```

The web app is a single file: open `docs/index.html` in a browser.

## Updating the data each month

1. Download the new CPI release from stat.uz (published early the following month).
2. Add 14 rows (headline + 13 divisions) to `data/raw/stat_uz_cpi_releases.csv` with the values as printed and the URL.
3. Run `python scripts/build_series.py` and `pytest -q`.
4. In the web app, upload `data/processed/cpi_divisions.csv` on the *Methodology & data* tab, or update the embedded data in `docs/index.html`.
5. Compare last month's forecast with the actual value and log it in `CHANGELOG.md`.

## Publishing the demo

Settings → Pages → Source: *Deploy from a branch* → Branch `main`, folder `/docs` → Save. The site appears at `https://<username>.github.io/<repo-name>/` within a few minutes.

## Roadmap

- [x] Basket builder, personal inflation, contributions, gap decomposition
- [x] Salary and purchasing power
- [x] Forecast with walk-forward backtest
- [x] Scenario lab
- [x] Official data pipeline with checks
- [ ] LLM explanation layer (receives only computed metrics; no advice; RU/UZ/EN)
- [ ] User testing: 15–30 participants, pre/post quiz with a control group (chart only vs chart + explanation)
- [ ] Regional view (regional headline CPI is in the same releases)
- [ ] Estimate exchange-rate pass-through from data instead of assumptions
- [ ] Research brief (5–8 pages)

## Use of AI tools

The initial scaffold of this repository (code structure, tests, web app) was produced with the help of an AI assistant (Claude). The research question, data verification, methodology decisions and all results are reviewed and maintained by the author. AI-generated code is covered by tests.

## Author

Amirkhon, Founder & Economics Research Lead. Project developed with Entrium mentorship.
