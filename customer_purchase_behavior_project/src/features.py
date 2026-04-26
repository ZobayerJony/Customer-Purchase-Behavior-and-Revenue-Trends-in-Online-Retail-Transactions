from typing import Tuple

import numpy as np
import pandas as pd


def _categorize_basket_value(value: float, low_cutoff: float, high_cutoff: float) -> str:
    """Assign a basket value category using percentile cutoffs."""
    if value <= low_cutoff:
        return "Low"
    if value <= high_cutoff:
        return "Medium"
    return "High"


def add_retail_features(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features required by the brief.

    New features include:
    - total_revenue
    - invoice_month
    - invoice_year
    - invoice_day_name
    - invoice_hour
    - market_group
    - day_type
    - basket_value
    - basket_distinct_items
    - basket_value_category
    - line_revenue_zscore
    """
    df = sales_df.copy()

    # Feature 1: revenue per transaction line.
    df["total_revenue"] = df["quantity"] * df["unit_price"]

    # Date-based features.
    df["invoice_month"] = df["invoice_date"].dt.to_period("M").astype(str)
    df["invoice_year"] = df["invoice_date"].dt.year
    df["invoice_day_name"] = df["invoice_date"].dt.day_name()
    df["invoice_hour"] = df["invoice_date"].dt.hour

    # Subgroup feature: domestic vs international market.
    df["market_group"] = np.where(
        df["country"].eq("United Kingdom"), "United Kingdom", "International"
    )

    # Subgroup feature: weekday vs weekend.
    df["day_type"] = np.where(df["invoice_date"].dt.dayofweek >= 5, "Weekend", "Weekday")

    # Invoice-level basket features mapped back to every line item.
    invoice_totals = df.groupby("invoice_no")["total_revenue"].sum()
    distinct_items = df.groupby("invoice_no")["stock_code"].nunique()

    df["basket_value"] = df["invoice_no"].map(invoice_totals)
    df["basket_distinct_items"] = df["invoice_no"].map(distinct_items)

    # Percentile-based basket categories using NumPy.
    invoice_total_values = invoice_totals.to_numpy(dtype=float)
    low_cutoff, high_cutoff = np.percentile(invoice_total_values, [33.33, 66.67])

    df["basket_value_category"] = df["basket_value"].apply(
        lambda value: _categorize_basket_value(value, low_cutoff, high_cutoff)
    )

    # NumPy-based z-score for line-level revenue.
    revenue_array = df["total_revenue"].to_numpy(dtype=float)
    revenue_mean = np.mean(revenue_array)
    revenue_std = np.std(revenue_array)

    if revenue_std == 0:
        df["line_revenue_zscore"] = 0.0
    else:
        df["line_revenue_zscore"] = (revenue_array - revenue_mean) / revenue_std

    return df