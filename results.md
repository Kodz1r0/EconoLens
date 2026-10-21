# Results (2024-08 .. 2026-09)

## 12-month inflation by basket

| Basket | Inflation | Gap vs official, p.p. | Largest gap driver |
|---|---|---|---|
| official (estimated weights) | 6.33% | - | - |
| student | 6.23% | -0.10 | housing (-0.19) |
| family_with_children | 6.38% | +0.06 | insurance (-0.11) |
| pensioner | 6.62% | +0.29 | housing (+0.36) |

## Forecast backtest (official basket, 1 month ahead, last 12 months)

| Method | How it works | MAE, p.p. | RMSE, p.p. |
|---|---|---|---|
| mean_12m | average monthly change over the last 12 months | 0.196 | 0.266 |
| naive | next month = last month | 0.263 | 0.361 |
| seasonal_naive | same month one year ago | 0.330 | 0.495 |

Chosen method: **mean_12m**. Next 3 months: +1.55% (95% band +0.65% .. +2.45%).
