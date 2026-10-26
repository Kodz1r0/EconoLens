# Data dictionary

## Source

Agency of Statistics under the President of the Republic of Uzbekistan, monthly press releases "Индекс потребительских цен" (Consumer Price Index). Classification: КИПЦ РУ 2018, 13 divisions. Every row in `data/raw/` carries the URL of the release it was copied from.

## `data/raw/stat_uz_cpi_releases.csv`

Values copied exactly as printed (percent, previous period = 100).

| Column | Type | Meaning |
|---|---|---|
| `release_month` | YYYY-MM | Month the release describes |
| `division` | text | `headline` or a division id (see below) |
| `mom` | number | Index to previous month, % (e.g. 100.7 = +0.7%) |
| `ytd` | number | Index to December of the previous year, % |
| `yoy` | number | Index to the same month of the previous year, % (in December releases equal to `ytd`) |
| `source_url` | URL | PDF release on stat.uz |

The September 2026 release does not print headline `ytd` in the division table, so that cell is empty.

## `data/raw/stat_uz_contributions.csv`

| Column | Meaning |
|---|---|
| `release_month` | Release the values come from |
| `period` | `ytd`: contribution to the change since December |
| `division` | Division id |
| `contribution_pp` | Contribution to headline CPI change, percentage points |
| `source_url` | Release URL |

## `data/processed/cpi_divisions.csv`

Monthly index level by division. **December 2024 = 100.** One row per month, Aug 2024 – Sep 2026, no gaps.

| Column | Division (EN) | Раздел (RU) |
|---|---|---|
| `month` | Month, YYYY-MM | |
| `food` | Food and non-alcoholic beverages | Продукты питания и безалкогольные напитки |
| `alcohol` | Alcoholic beverages and tobacco | Алкогольные напитки и табачные изделия |
| `clothing` | Clothing and footwear | Одежда и обувь |
| `housing` | Housing, water, electricity, gas and other fuels | Жилищные услуги, вода, электричество, газ и другие виды топлива |
| `furnishings` | Furnishings, household equipment, maintenance | Предметы домашнего обихода, бытовая техника и текущее обслуживание жилья |
| `health` | Health | Здравоохранение |
| `transport` | Transport | Транспорт |
| `communication` | Information and communication | Информация и связь |
| `recreation` | Recreation, sport and culture | Отдых, спорт и культура |
| `education` | Education services | Услуги в области образования |
| `restaurants` | Restaurants and accommodation | Рестораны и гостиничное обслуживание |
| `insurance` | Insurance and financial services | Страхование и финансовые услуги |
| `misc` | Miscellaneous goods and services | Бытовые товары и услуги, разные товары и услуги |

### Construction rules (level L, Dec 2024 = 100)

1. Aug–Dec 2025: `L = ytd` from the release for that month.
2. 2026: `L = L(Dec 2025) × ytd / 100`.
3. Jan–Jul 2025: `L = L(same month 2026) / yoy(2026 release) × 100`.
4. Aug–Nov 2024: `L = L(same month 2025) / yoy(2025 release) × 100`.

Levels are not chained from month-on-month values, so rounding errors do not accumulate.

## `data/processed/official_weights_estimated.csv`

| Column | Meaning |
|---|---|
| `division` | Division id |
| `weight_pct` | Estimated share of the division in the official CPI basket, 2026, % (sums to 100) |

Estimated as `contribution_ytd / (ytd − 100)` from the September 2026 release, then normalised. Not an official publication.
