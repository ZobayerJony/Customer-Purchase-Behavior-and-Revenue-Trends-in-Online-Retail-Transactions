import json
from typing import Tuple, Dict, Any

import numpy as np
import pandas as pd

from .config import CLEANING_LOG_FILE


COLUMN_RENAME_MAP = {
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "UnitPrice": "unit_price",
    "CustomerID": "customer_id",
    "Country": "country",
}


def _clean_customer_id(series: pd.Series) -> pd.Series:
    """
    Convert customer IDs from Excel-style float values to clean string IDs.
    Missing customer IDs remain missing.
    """
    numeric_ids = pd.to_numeric(series, errors="coerce")
    return numeric_ids.astype("Int64").astype("string")


def clean_retail_data(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Clean the Online Retail dataset for revenue and customer behavior analysis.

    Cleaning/preprocessing steps:
    1. Standardize column names.
    2. Convert data types, including invoice_date as datetime.
    3. Remove exact duplicate rows.
    4. Identify cancelled/returned transactions.
    5. Keep only valid sales rows with positive quantity and price.
    6. Clean text columns and handle missing product descriptions.
    """
    df = raw_df.copy()
    original_rows = len(df)

    # Step 1: standardize column names.
    df.columns = df.columns.str.strip()
    df = df.rename(columns=COLUMN_RENAME_MAP)

    # Step 2: convert data types.
    text_columns = ["invoice_no", "stock_code", "description", "country"]
    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["customer_id"] = _clean_customer_id(df["customer_id"])

    rows_with_invalid_date = int(df["invoice_date"].isna().sum())

    # Step 3: remove exact duplicates.
    duplicate_rows = int(df.duplicated().sum())
    df = df.drop_duplicates()

    # Step 4: identify cancelled/returned transactions.
    df["is_cancelled_invoice"] = df["invoice_no"].str.startswith("C", na=False)
    df["is_return_or_invalid_quantity"] = df["quantity"] <= 0
    df["is_invalid_price"] = df["unit_price"] <= 0

    cancelled_or_return_rows = int(
        (
            df["is_cancelled_invoice"]
            | df["is_return_or_invalid_quantity"]
            | df["is_invalid_price"]
        ).sum()
    )

    # Step 5: keep positive completed sales for the main analysis.
    sales_df = df[
        (~df["is_cancelled_invoice"])
        & (df["quantity"] > 0)
        & (df["unit_price"] > 0)
        & (df["invoice_date"].notna())
    ].copy()

    # Step 6: clean descriptions and country values.
    sales_df["description"] = sales_df["description"].fillna("Unknown Product")
    sales_df["description"] = (
        sales_df["description"]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    sales_df["country"] = sales_df["country"].fillna("Unknown Country")

    rows_removed_from_sales_analysis = original_rows - len(sales_df)

    cleaning_log: Dict[str, Any] = {
        "original_rows": int(original_rows),
        "rows_after_duplicate_removal": int(len(df)),
        "duplicate_rows_removed": int(duplicate_rows),
        "rows_with_invalid_invoice_date": int(rows_with_invalid_date),
        "cancelled_or_return_rows_identified": int(cancelled_or_return_rows),
        "rows_removed_from_sales_analysis": int(rows_removed_from_sales_analysis),
        "analysis_ready_rows": int(len(sales_df)),
        "missing_customer_id_rows_in_sales_data": int(sales_df["customer_id"].isna().sum()),
        "cleaning_justification": [
            {
                "step": "Standardized column names",
                "reason": "Lowercase snake_case names are easier and safer to use in Python code.",
            },
            {
                "step": "Converted data types",
                "reason": "Dates and numeric fields must have correct types before time-series and revenue calculations.",
            },
            {
                "step": "Removed exact duplicate rows",
                "reason": "Duplicates can overstate sales revenue and transaction counts.",
            },
            {
                "step": "Separated cancelled/returned transactions",
                "reason": "The project focuses on positive completed sales, so cancellations and returns are excluded from the main analysis.",
            },
            {
                "step": "Kept only positive quantities and prices",
                "reason": "Revenue trend analysis requires valid sales values.",
            },
            {
                "step": "Cleaned product descriptions",
                "reason": "Consistent product names improve product-level grouping and charts.",
            },
        ],
    }

    with open(CLEANING_LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(cleaning_log, file, indent=4)

    return sales_df, cleaning_log