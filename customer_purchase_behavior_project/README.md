# Customer Purchase Behavior and Revenue Trends in Online Retail Transactions

## Project title
**Customer Purchase Behavior and Revenue Trends in Online Retail Transactions**

## Project objective
This project investigates transaction-level online retail data to understand revenue trends, customer purchasing behavior, product performance, country-level differences, and unusual high-value transactions.

The project uses:

- **Pandas** for loading, cleaning, grouping, filtering, aggregating, and transforming data.
- **NumPy** for custom numerical calculations such as percentiles, z-scores, and correlation.
- **Matplotlib** for meaningful charts that support the analysis questions.

## Dataset
**Dataset name:** Online Retail  
**Source:** UCI Machine Learning Repository  
**Source page:** https://archive.ics.uci.edu/dataset/352/online+retail  
**Direct file URL:** https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx  
**Citation:** Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33

The dataset contains transactions from a UK-based non-store online retailer between 01/12/2010 and 09/12/2011.

## Analytical questions
1. How does online retail revenue change over time?
2. Which countries and products contribute most to total revenue?
3. What patterns exist in customer purchase behavior, and which transactions look unusually large?

## Project structure

```text
customer_purchase_behavior_project/
│
├── README.md
├── requirements.txt
├── run_project.py
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── Online_Retail.xlsx              # downloaded automatically
│   └── processed/
│       └── cleaned_online_retail.csv       # generated after running
│
├── notebooks/
│   └── Customer_Purchase_Behavior_Analysis.ipynb
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── cleaning.py
│   ├── features.py
│   ├── analysis.py
│   ├── visualization.py
│   └── report_generator.py
│
├── scripts/
│   └── download_data.py
│
├── outputs/
│   ├── figures/                            # generated charts
│   └── tables/                             # generated summary tables
│
└── report/
    ├── REPORT_INSTRUCTIONS.md
    ├── Final_Project_Report.md             # generated after running
    └── Final_Project_Report.docx           # generated after running
```

## How to run locally

### Step 1: Unzip the project
Open a terminal or command prompt inside the project folder.

```bash
cd customer_purchase_behavior_project
```

### Step 2: Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install required libraries

```bash
pip install -r requirements.txt
```

### Step 4: Run the full project

Replace the example name and ID with your own information.

```bash
python run_project.py --name "Your Name" --student-id "Your Student ID"
```

This command will:

1. Download the UCI Online Retail Excel dataset.
2. Load and inspect the raw dataset.
3. Clean and prepare the data.
4. Create engineered features.
5. Run all required analyses.
6. Create Matplotlib visualizations.
7. Save summary tables and figures.
8. Generate a final Markdown report.
9. Try to generate a DOCX report if `python-docx` is installed.

## How to run in Google Colab

1. Upload this project folder to Google Drive or GitHub.
2. Open `notebooks/Customer_Purchase_Behavior_Analysis.ipynb`.
3. Run the first setup cell.
4. Run each cell from top to bottom.
5. Download the generated report and figures from the `report/` and `outputs/` folders.

## Important generated files

After running the project, check these files:

```text
data/processed/cleaned_online_retail.csv
outputs/tables/monthly_revenue_summary.csv
outputs/tables/country_revenue_summary.csv
outputs/tables/top_products_summary.csv
outputs/tables/customer_behavior_summary.csv
outputs/tables/invoice_outliers.csv
outputs/figures/01_monthly_revenue_trend.png
outputs/figures/02_top_countries_by_revenue.png
outputs/figures/03_top_products_by_revenue.png
outputs/figures/04_invoice_value_distribution.png
outputs/figures/05_invoice_items_vs_value_relationship.png
outputs/figures/06_market_group_boxplot.png
report/Final_Project_Report.md
report/Final_Project_Report.docx
```

## What to submit

Submit either:

- A public GitHub repository containing this project after running it, or
- A Google Colab notebook link that runs successfully.

Also submit the generated report separately if your instructor asks for a report upload.

## Viva preparation
Read `PROJECT_GUIDE_STEP_BY_STEP.md` before your viva. It explains why each step exists and how to answer common questions.