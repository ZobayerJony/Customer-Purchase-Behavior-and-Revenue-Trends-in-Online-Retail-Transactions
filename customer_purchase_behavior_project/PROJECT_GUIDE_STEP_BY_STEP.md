# Step-by-step explanation of the full project

## 1. Why this dataset was selected

The selected dataset is the **Online Retail** dataset from the UCI Machine Learning Repository. It is appropriate because it is real, credible, large, and business-focused. It has more than 1000 rows and more than 6 columns, and it includes date/time, numeric, and categorical variables.

The dataset supports the project title:

**Customer Purchase Behavior and Revenue Trends in Online Retail Transactions**

It contains transaction records, product details, quantities, prices, customer IDs, dates, and countries. This makes it suitable for revenue trend analysis, product ranking, country comparison, customer behavior analysis, and outlier detection.

## 2. Main analytical questions

The project answers three questions:

1. **How does online retail revenue change over time?**  
   This is answered using monthly revenue trend analysis.

2. **Which countries and products contribute most to total revenue?**  
   This is answered using country-level and product-level groupby analysis.

3. **What patterns exist in customer purchase behavior, and which transactions look unusually large?**  
   This is answered using customer summaries, invoice-level basket analysis, relationship analysis, and outlier detection.

## 3. Data loading

The script `run_project.py` calls `download_dataset()` from `src/data_loader.py`.

That function downloads the Excel file from the UCI Machine Learning Repository and stores it in:

```text
data/raw/Online_Retail.xlsx
```

Then Pandas loads it using:

```python
pd.read_excel(path, engine="openpyxl")
```

## 4. Data understanding

The project saves these data-understanding outputs:

```text
outputs/tables/data_types_and_missing_values.csv
outputs/tables/sample_rows.csv
outputs/tables/numeric_summary_statistics.csv
outputs/data_profile.json
```

These files show:

- dataset shape
- column names
- data types
- missing values
- sample rows
- summary statistics
- duplicate rows

This section satisfies the project brief requirement for dataset inspection.

## 5. Data cleaning

The cleaning function is in:

```text
src/cleaning.py
```

The main cleaning steps are:

### Step 1: Standardize column names

Original names such as `InvoiceNo` and `UnitPrice` are renamed to `invoice_no` and `unit_price`.

Reason: cleaner names reduce code mistakes and make analysis easier.

### Step 2: Convert data types

The project converts:

- `invoice_date` to datetime
- `quantity` to numeric
- `unit_price` to numeric
- `customer_id` to clean string ID

Reason: date analysis, revenue calculation, and customer grouping require correct data types.

### Step 3: Remove duplicate rows

Duplicate rows are removed because they can overstate revenue and product sales.

### Step 4: Remove cancellations and invalid sales rows

Invoice numbers starting with `C`, negative quantities, zero quantities, and non-positive prices are removed from the main positive-sales dataset.

Reason: the project focuses on completed sales and customer purchases, not refunds or cancellations.

### Step 5: Clean text values

Product descriptions and countries are stripped of extra spaces, and missing product descriptions are labeled as `UNKNOWN PRODUCT`.

Reason: clean text supports accurate grouping.

## 6. Feature engineering

Feature engineering is done in:

```text
src/features.py
```

Important derived features:

| Feature | Meaning | Why it matters |
|---|---|---|
| `total_revenue` | quantity × unit_price | Main revenue measure |
| `invoice_month` | month extracted from date | Monthly trend analysis |
| `invoice_hour` | hour extracted from date | Time behavior analysis |
| `market_group` | UK or International | Subgroup comparison |
| `day_type` | Weekday or Weekend | Subgroup comparison |
| `basket_value` | invoice-level total | Order value analysis |
| `basket_distinct_items` | number of products in invoice | Relationship analysis |
| `basket_value_category` | low/medium/high order value | NumPy percentile-based grouping |
| `line_revenue_zscore` | standardized revenue score | Outlier support |

This satisfies the requirement for at least two derived columns.

## 7. Data analysis

Analysis is performed in:

```text
src/analysis.py
```

The project includes more than six meaningful analysis operations:

1. Overall KPI summary
2. Monthly revenue trend
3. Country revenue ranking
4. Product revenue ranking
5. Customer purchase behavior summary
6. UK vs international subgroup comparison
7. Weekday vs weekend subgroup comparison
8. Relationship analysis between basket size and invoice value
9. Outlier detection using IQR and z-scores

## 8. NumPy usage

NumPy is used meaningfully for:

- percentile calculations
- z-score calculation
- correlation calculation
- outlier thresholds

Examples:

```python
np.percentile(invoice_values, [25, 75])
np.corrcoef(x_arr, y_arr)
np.mean(values)
np.std(values)
```

This satisfies the brief requirement that NumPy must be used for actual numerical work, not only imported.

## 9. Visualizations

The project creates six Matplotlib charts:

```text
outputs/figures/01_monthly_revenue_trend.png
outputs/figures/02_top_countries_by_revenue.png
outputs/figures/03_top_products_by_revenue.png
outputs/figures/04_invoice_value_distribution.png
outputs/figures/05_invoice_items_vs_value_relationship.png
outputs/figures/06_market_group_boxplot.png
```

These charts cover:

- trend analysis
- ranking analysis
- distribution analysis
- relationship analysis
- subgroup comparison
- outlier context

The project brief requires at least four charts, so this project exceeds the requirement.

## 10. Report generation

The final report is generated by:

```text
src/report_generator.py
```

After running the project, the final report is saved as:

```text
report/Final_Project_Report.md
report/Final_Project_Report.docx
```

The report automatically includes:

- title
- student name and ID
- dataset source and citation
- objective
- questions
- cleaning explanation
- engineered features
- visualizations
- findings
- limitations
- conclusion

## 11. How to explain this project in viva

### Why did you choose this dataset?

Because it is real, credible, large, and suitable for business analysis. It contains dates, countries, customers, products, quantities, and prices.

### Why did you remove cancellations?

The main project studies completed positive sales. Cancellations and returns would reduce revenue and represent a different business question.

### Why did you create `total_revenue`?

The original dataset has quantity and unit price separately. Revenue is needed to answer sales and business-performance questions.

### Why did you create `market_group`?

The company is UK-based, so comparing United Kingdom and international transactions is meaningful.

### Why did you use outlier analysis?

Some customers are wholesalers, so some invoices may be much larger than typical retail purchases. Outlier analysis helps identify unusual high-value invoices.

### What is a limitation of the project?

Customer IDs are missing for some rows, and the dataset covers only a limited period. Also, correlation does not prove causation.

## 12. Final submission checklist

Before submitting, confirm that:

- the code runs without errors
- the dataset source is mentioned
- the report has your name and student ID
- the report includes figures
- the GitHub or Colab link is accessible
- you understand the cleaning and feature engineering steps