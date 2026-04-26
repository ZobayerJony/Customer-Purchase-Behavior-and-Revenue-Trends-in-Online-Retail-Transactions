import json
from typing import Dict, Any

import numpy as np
import pandas as pd

from .config import (
    TABLES_DIR,
    ANALYSIS_RESULTS_FILE,
)


def _to_builtin(value):
    """Convert NumPy/Pandas values to JSON-serializable Python values."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value):
            return None
        return float(value)
    if isinstance(value, (np.ndarray,)):
        return value.tolist()
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def _safe_corr(x: pd.Series, y: pd.Series) -> float:
    """Compute a NumPy correlation safely."""
    x_arr = x.to_numpy(dtype=float)
    y_arr = y.to_numpy(dtype=float)

    if len(x_arr) < 2 or np.std(x_arr) == 0 or np.std(y_arr) == 0:
        return float("nan")

    return float(np.corrcoef(x_arr, y_arr)[0, 1])


def run_all_analyses(raw_df: pd.DataFrame, sales_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Run all analysis operations required in the project brief and save summary tables.

    Analysis operations included:
    1. Overall KPI summary
    2. Monthly revenue trend analysis
    3. Country-level revenue ranking
    4. Product-level revenue ranking
    5. Customer behavior summary
    6. Domestic vs international subgroup comparison
    7. Weekday vs weekend subgroup comparison
    8. Relationship analysis between basket size and invoice value
    9. Outlier/anomaly analysis using NumPy percentiles and IQR
    """
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Invoice-level table for several analyses.
    invoice_level = (
        sales_df.groupby("invoice_no")
        .agg(
            invoice_date=("invoice_date", "min"),
            invoice_month=("invoice_month", "first"),
            country=("country", "first"),
            market_group=("market_group", "first"),
            day_type=("day_type", "first"),
            invoice_total=("total_revenue", "sum"),
            total_units=("quantity", "sum"),
            distinct_items=("stock_code", "nunique"),
            customer_id=("customer_id", "first"),
        )
        .reset_index()
    )

    invoice_level.to_csv(TABLES_DIR / "invoice_level_summary.csv", index=False)

    # 1. Overall KPI summary.
    total_revenue = float(sales_df["total_revenue"].sum())
    total_orders = int(sales_df["invoice_no"].nunique())
    total_units = int(sales_df["quantity"].sum())
    unique_customers = int(sales_df["customer_id"].nunique(dropna=True))
    unique_products = int(sales_df["stock_code"].nunique())
    unique_countries = int(sales_df["country"].nunique())

    # 2. Monthly trend.
    monthly = (
        sales_df.groupby("invoice_month")
        .agg(
            total_revenue=("total_revenue", "sum"),
            orders=("invoice_no", "nunique"),
            units_sold=("quantity", "sum"),
            unique_customers=("customer_id", "nunique"),
        )
        .reset_index()
        .sort_values("invoice_month")
    )
    monthly["average_order_value"] = monthly["total_revenue"] / monthly["orders"]
    monthly.to_csv(TABLES_DIR / "monthly_revenue_summary.csv", index=False)

    # 3. Country ranking.
    country = (
        sales_df.groupby("country")
        .agg(
            total_revenue=("total_revenue", "sum"),
            orders=("invoice_no", "nunique"),
            units_sold=("quantity", "sum"),
            unique_customers=("customer_id", "nunique"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    country["revenue_share_percent"] = country["total_revenue"] / total_revenue * 100
    country["average_order_value"] = country["total_revenue"] / country["orders"]
    country.to_csv(TABLES_DIR / "country_revenue_summary.csv", index=False)

    # 4. Product ranking.
    product = (
        sales_df.groupby("description")
        .agg(
            total_revenue=("total_revenue", "sum"),
            units_sold=("quantity", "sum"),
            orders=("invoice_no", "nunique"),
            average_unit_price=("unit_price", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    product.to_csv(TABLES_DIR / "top_products_summary.csv", index=False)

    # 5. Customer behavior.
    known_customers = sales_df.dropna(subset=["customer_id"]).copy()
    customer = (
        known_customers.groupby("customer_id")
        .agg(
            total_spent=("total_revenue", "sum"),
            orders=("invoice_no", "nunique"),
            total_units=("quantity", "sum"),
            first_purchase=("invoice_date", "min"),
            last_purchase=("invoice_date", "max"),
        )
        .reset_index()
        .sort_values("total_spent", ascending=False)
    )
    customer["average_order_value"] = customer["total_spent"] / customer["orders"]
    customer["active_days"] = (customer["last_purchase"] - customer["first_purchase"]).dt.days + 1

    if len(customer) > 0:
        low_cutoff, high_cutoff = np.percentile(customer["total_spent"].to_numpy(dtype=float), [33.33, 66.67])
        customer["customer_value_segment"] = np.select(
            [
                customer["total_spent"] <= low_cutoff,
                customer["total_spent"] <= high_cutoff,
            ],
            ["Low", "Medium"],
            default="High",
        )
    else:
        customer["customer_value_segment"] = []

    customer.to_csv(TABLES_DIR / "customer_behavior_summary.csv", index=False)

    # 6. Subgroup comparison: United Kingdom vs International.
    market_group = (
        invoice_level.groupby("market_group")
        .agg(
            total_revenue=("invoice_total", "sum"),
            orders=("invoice_no", "nunique"),
            average_order_value=("invoice_total", "mean"),
            median_order_value=("invoice_total", "median"),
            average_distinct_items=("distinct_items", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    market_group["revenue_share_percent"] = market_group["total_revenue"] / market_group["total_revenue"].sum() * 100
    market_group.to_csv(TABLES_DIR / "market_group_comparison.csv", index=False)

    # 7. Subgroup comparison: Weekday vs Weekend.
    day_type = (
        invoice_level.groupby("day_type")
        .agg(
            total_revenue=("invoice_total", "sum"),
            orders=("invoice_no", "nunique"),
            average_order_value=("invoice_total", "mean"),
            median_order_value=("invoice_total", "median"),
            average_distinct_items=("distinct_items", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    day_type["revenue_share_percent"] = day_type["total_revenue"] / day_type["total_revenue"].sum() * 100
    day_type.to_csv(TABLES_DIR / "weekday_weekend_comparison.csv", index=False)

    # 8. Relationship analysis between basket size and invoice value.
    basket_value_corr = _safe_corr(invoice_level["distinct_items"], invoice_level["invoice_total"])
    unit_value_corr = _safe_corr(invoice_level["total_units"], invoice_level["invoice_total"])

    relationship_summary = pd.DataFrame(
        [
            {
                "relationship": "Distinct products in invoice vs invoice total",
                "correlation": basket_value_corr,
                "interpretation": "Positive values mean invoices with more distinct products usually have higher value.",
            },
            {
                "relationship": "Total units in invoice vs invoice total",
                "correlation": unit_value_corr,
                "interpretation": "Positive values mean invoices with more units usually have higher value.",
            },
        ]
    )
    relationship_summary.to_csv(TABLES_DIR / "relationship_analysis.csv", index=False)

    # 9. Outlier analysis using NumPy.
    invoice_values = invoice_level["invoice_total"].to_numpy(dtype=float)
    q1, q3 = np.percentile(invoice_values, [25, 75])
    iqr = q3 - q1
    upper_outlier_limit = q3 + 1.5 * iqr
    p90, p95, p99 = np.percentile(invoice_values, [90, 95, 99])
    mean_invoice_value = float(np.mean(invoice_values))
    std_invoice_value = float(np.std(invoice_values))

    if std_invoice_value == 0:
        z_scores = np.zeros_like(invoice_values)
    else:
        z_scores = (invoice_values - mean_invoice_value) / std_invoice_value

    invoice_level["invoice_value_zscore"] = z_scores
    invoice_level["is_high_value_outlier_iqr"] = invoice_level["invoice_total"] > upper_outlier_limit
    invoice_level["is_high_value_outlier_zscore"] = invoice_level["invoice_value_zscore"] > 3

    outliers = invoice_level.loc[invoice_level["is_high_value_outlier_iqr"]].sort_values(
        "invoice_total", ascending=False
    )
    outliers.to_csv(TABLES_DIR / "invoice_outliers.csv", index=False)

    # Key metrics for the report.
    top_country_row = country.iloc[0]
    top_product_row = product.iloc[0]
    best_month_row = monthly.sort_values("total_revenue", ascending=False).iloc[0]

    uk_share = 0.0
    if "United Kingdom" in set(market_group["market_group"]):
        uk_share = float(
            market_group.loc[
                market_group["market_group"].eq("United Kingdom"), "revenue_share_percent"
            ].iloc[0]
        )

    weekday_aov = None
    weekend_aov = None
    if "Weekday" in set(day_type["day_type"]):
        weekday_aov = float(day_type.loc[day_type["day_type"].eq("Weekday"), "average_order_value"].iloc[0])
    if "Weekend" in set(day_type["day_type"]):
        weekend_aov = float(day_type.loc[day_type["day_type"].eq("Weekend"), "average_order_value"].iloc[0])

    key_metrics = {
        "raw_rows": int(raw_df.shape[0]),
        "raw_columns": int(raw_df.shape[1]),
        "analysis_ready_rows": int(sales_df.shape[0]),
        "analysis_ready_columns": int(sales_df.shape[1]),
        "date_min": str(sales_df["invoice_date"].min().date()),
        "date_max": str(sales_df["invoice_date"].max().date()),
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_units": total_units,
        "unique_customers": unique_customers,
        "unique_products": unique_products,
        "unique_countries": unique_countries,
        "average_order_value": total_revenue / total_orders,
        "top_country": str(top_country_row["country"]),
        "top_country_revenue": float(top_country_row["total_revenue"]),
        "top_country_share_percent": float(top_country_row["revenue_share_percent"]),
        "top_product": str(top_product_row["description"]),
        "top_product_revenue": float(top_product_row["total_revenue"]),
        "best_month": str(best_month_row["invoice_month"]),
        "best_month_revenue": float(best_month_row["total_revenue"]),
        "uk_revenue_share_percent": uk_share,
        "weekday_average_order_value": weekday_aov,
        "weekend_average_order_value": weekend_aov,
        "basket_value_correlation_distinct_items": basket_value_corr,
        "basket_value_correlation_total_units": unit_value_corr,
        "invoice_value_q1": float(q1),
        "invoice_value_q3": float(q3),
        "invoice_value_iqr": float(iqr),
        "invoice_value_upper_outlier_limit": float(upper_outlier_limit),
        "invoice_value_p90": float(p90),
        "invoice_value_p95": float(p95),
        "invoice_value_p99": float(p99),
        "high_value_outlier_count_iqr": int(outliers.shape[0]),
        "high_value_outlier_share_percent": float(outliers.shape[0] / invoice_level.shape[0] * 100),
    }

    results = {
        "key_metrics": key_metrics,
        "tables": {
            "monthly": "outputs/tables/monthly_revenue_summary.csv",
            "country": "outputs/tables/country_revenue_summary.csv",
            "product": "outputs/tables/top_products_summary.csv",
            "customer": "outputs/tables/customer_behavior_summary.csv",
            "market_group": "outputs/tables/market_group_comparison.csv",
            "day_type": "outputs/tables/weekday_weekend_comparison.csv",
            "relationship": "outputs/tables/relationship_analysis.csv",
            "outliers": "outputs/tables/invoice_outliers.csv",
        },
    }

    with open(ANALYSIS_RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, default=_to_builtin)

    return results
