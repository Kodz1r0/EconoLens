"""Division metadata and data loading for EconoLens Uzbekistan."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_RELEASES = ROOT / "data" / "raw" / "stat_uz_cpi_releases.csv"
RAW_CONTRIBUTIONS = ROOT / "data" / "raw" / "stat_uz_contributions.csv"
SERIES = ROOT / "data" / "processed" / "cpi_divisions.csv"
WEIGHTS = ROOT / "data" / "processed" / "official_weights_estimated.csv"

# 13 divisions of the national CPI classification (КИПЦ РУ 2018), in official order.
DIVISIONS = [
    ("food", "Food and non-alcoholic beverages", "Продукты питания и безалкогольные напитки"),
    ("alcohol", "Alcoholic beverages and tobacco", "Алкогольные напитки и табачные изделия"),
    ("clothing", "Clothing and footwear", "Одежда и обувь"),
    ("housing", "Housing, water, electricity, gas and other fuels", "Жилищные услуги, вода, электричество, газ и другие виды топлива"),
    ("furnishings", "Furnishings, household equipment and maintenance", "Предметы домашнего обихода, бытовая техника и текущее обслуживание жилья"),
    ("health", "Health", "Здравоохранение"),
    ("transport", "Transport", "Транспорт"),
    ("communication", "Information and communication", "Информация и связь"),
    ("recreation", "Recreation, sport and culture", "Отдых, спорт и культура"),
    ("education", "Education services", "Услуги в области образования"),
    ("restaurants", "Restaurants and accommodation services", "Рестораны и гостиничное обслуживание"),
    ("insurance", "Insurance and financial services", "Страхование и финансовые услуги"),
    ("misc", "Personal care, social protection and miscellaneous", "Бытовые товары и услуги, разные товары и услуги"),
]
DIVISION_IDS = [d[0] for d in DIVISIONS]


def load_series(path: Path | str = SERIES) -> pd.DataFrame:
    """Monthly index levels by division (Dec 2024 = 100), indexed by month 'YYYY-MM'."""
    df = pd.read_csv(path, dtype={"month": str}).set_index("month")
    missing = [d for d in DIVISION_IDS if d not in df.columns]
    if missing:
        raise ValueError(f"Missing division columns: {missing}")
    return df[DIVISION_IDS].astype(float)


def load_official_weights(path: Path | str = WEIGHTS) -> pd.Series:
    """Estimated official CPI basket weights (shares summing to 1)."""
    w = pd.read_csv(path).set_index("division")["weight_pct"]
    return (w / w.sum()).reindex(DIVISION_IDS)
