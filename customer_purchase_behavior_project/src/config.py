from pathlib import Path

PROJECT_TITLE = "Customer Purchase Behavior and Revenue Trends in Online Retail Transactions"

# Student information can be passed from the command line in run_project.py.
DEFAULT_STUDENT_NAME = "Your Name"
DEFAULT_STUDENT_ID = "Your Student ID"

# Dataset source information
DATASET_NAME = "Online Retail"
DATASET_SOURCE_PAGE = "https://archive.ics.uci.edu/dataset/352/online+retail"
DATASET_DIRECT_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
DATASET_CITATION = (
    "Chen, D. (2015). Online Retail [Dataset]. "
    "UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33"
)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"
REPORT_DIR = PROJECT_ROOT / "report"

RAW_DATA_FILE = RAW_DATA_DIR / "Online_Retail.xlsx"
CLEANED_DATA_FILE = PROCESSED_DATA_DIR / "cleaned_online_retail.csv"
ANALYSIS_RESULTS_FILE = OUTPUTS_DIR / "analysis_results.json"
CLEANING_LOG_FILE = OUTPUTS_DIR / "cleaning_log.json"

# Expected original columns from the UCI Online Retail dataset
EXPECTED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]