from pathlib import Path
import textwrap
from typing import Dict

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import FIGURES_DIR, TABLES_DIR


def _shorten_label(label: str, width: int = 35) -> str:
    """Shorten long product names for readable charts."""
    return textwrap.shorten(str(label), width=width, placeholder="...")


def create_all_figures() -> Dict[str, str]:
    """
    Create all Matplotlib figures from the saved analysis tables.

    Returns a dictionary mapping figure names to file paths.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    monthly = pd.read_csv(TABLES_DIR / "monthly_revenue_summary.csv")
    country = pd.read_csv(TABLES_DIR / "country_revenue_summary.csv")
    product = pd.read_csv(TABLES_DIR / "top_products_summary.csv")
    invoice_level = pd.read_csv(TABLES_DIR / "invoice_level_summary.csv")

    figure_paths: Dict[str, str] = {}

    # Figure 1: Monthly revenue trend.
    monthly["month_date"] = pd.to_datetime(monthly["invoice_month"])
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly["month_date"], monthly["total_revenue"], marker="o")
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total revenue (£)")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    path = FIGURES_DIR / "01_monthly_revenue_trend.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    figure_paths["monthly_revenue_trend"] = str(path)

    # Figure 2: Top countries by revenue.
    top_country = country.head(10).sort_values("total_revenue", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_country["country"], top_country["total_revenue"])
    ax.set_title("Top 10 Countries by Revenue")
    ax.set_xlabel("Total revenue (£)")
    ax.set_ylabel("Country")
    fig.tight_layout()
    path = FIGURES_DIR / "02_top_countries_by_revenue.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    figure_paths["top_countries_by_revenue"] = str(path)

    # Figure 3: Top products by revenue.
    top_product = product.head(10).copy()
    top_product["product_label"] = top_product["description"].apply(_shorten_label)
    top_product = top_product.sort_values("total_revenue", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_product["product_label"], top_product["total_revenue"])
    ax.set_title("Top 10 Products by Revenue")
    ax.set_xlabel("Total revenue (£)")
    ax.set_ylabel("Product")
    fig.tight_layout()
    path = FIGURES_DIR / "03_top_products_by_revenue.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    figure_paths["top_products_by_revenue"] = str(path)

    # Figure 4: Invoice value distribution.
    invoice_values = invoice_level["invoice_total"].to_numpy(dtype=float)
    cap_99 = np.percentile(invoice_values, 99)
    trimmed_values = invoice_values[invoice_values <= cap_99]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(trimmed_values, bins=40)
    ax.set_title("Distribution of Invoice Values up to the 99th Percentile")
    ax.set_xlabel("Invoice value (£)")
    ax.set_ylabel("Number of invoices")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = FIGURES_DIR / "04_invoice_value_distribution.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    figure_paths["invoice_value_distribution"] = str(path)

    # Figure 5: Relationship between basket size and invoice value.
    relationship_df = invoice_level.loc[invoice_level["invoice_total"] <= cap_99].copy()
    if len(relationship_df) > 5000:
        relationship_df = relationship_df.sample(5000, random_state=42)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(
        relationship_df["distinct_items"],
        relationship_df["invoice_total"],
        alpha=0.35,
        s=14,
    )
    ax.set_title("Relationship Between Distinct Products and Invoice Value")
    ax.set_xlabel("Distinct products in invoice")
    ax.set_ylabel("Invoice value (£)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = FIGURES_DIR / "05_invoice_items_vs_value_relationship.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    figure_paths["invoice_items_vs_value_relationship"] = str(path)

    # Figure 6: Boxplot by market group.
    boxplot_df = invoice_level.loc[invoice_level["invoice_total"] <= cap_99].copy()
    labels = list(boxplot_df["market_group"].dropna().unique())
    data = [
        boxplot_df.loc[boxplot_df["market_group"].eq(label), "invoice_total"].to_numpy(dtype=float)
        for label in labels
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(data, labels=labels, showfliers=False)
    ax.set_title("Invoice Value Comparison: UK vs International")
    ax.set_xlabel("Market group")
    ax.set_ylabel("Invoice value (£)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    path = FIGURES_DIR / "06_market_group_boxplot.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    figure_paths["market_group_boxplot"] = str(path)

    return figure_paths
