import argparse

from src.config import (
    PROJECT_TITLE,
    DEFAULT_STUDENT_NAME,
    DEFAULT_STUDENT_ID,
    CLEANED_DATA_FILE,
)
from src.data_loader import (
    make_directories,
    download_dataset,
    load_raw_data,
    validate_dataset,
    create_data_understanding_outputs,
)
from src.cleaning import clean_retail_data
from src.features import add_retail_features
from src.analysis import run_all_analyses
from src.visualization import create_all_figures
from src.report_generator import generate_markdown_report, generate_docx_report


def parse_args():
    parser = argparse.ArgumentParser(description=PROJECT_TITLE)
    parser.add_argument("--name", default=DEFAULT_STUDENT_NAME, help="Student name for the report")
    parser.add_argument("--student-id", default=DEFAULT_STUDENT_ID, help="Student ID for the report")
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Download the dataset again even if it already exists",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 80)
    print(PROJECT_TITLE)
    print("=" * 80)

    make_directories()

    print("\n[1/8] Downloading or locating dataset...")
    dataset_path = download_dataset(force=args.force_download)

    print("\n[2/8] Loading raw dataset...")
    raw_df = load_raw_data(dataset_path)
    validate_dataset(raw_df)
    print(f"Raw dataset shape: {raw_df.shape[0]:,} rows × {raw_df.shape[1]:,} columns")

    print("\n[3/8] Creating data-understanding outputs...")
    create_data_understanding_outputs(raw_df)

    print("\n[4/8] Cleaning dataset...")
    sales_df, cleaning_log = clean_retail_data(raw_df)
    print(f"Analysis-ready dataset shape: {sales_df.shape[0]:,} rows × {sales_df.shape[1]:,} columns")

    print("\n[5/8] Engineering features...")
    sales_df = add_retail_features(sales_df)
    sales_df.to_csv(CLEANED_DATA_FILE, index=False)
    print(f"Saved cleaned dataset: {CLEANED_DATA_FILE}")

    print("\n[6/8] Running analysis...")
    results = run_all_analyses(raw_df, sales_df)
    print("Analysis completed.")

    print("\n[7/8] Creating visualizations...")
    figure_paths = create_all_figures()
    for name, path in figure_paths.items():
        print(f"Created {name}: {path}")

    print("\n[8/8] Generating report...")
    markdown_path = generate_markdown_report(args.name, args.student_id)
    docx_path = generate_docx_report(args.name, args.student_id)

    print("\n" + "=" * 80)
    print("PROJECT COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Cleaned dataset: {CLEANED_DATA_FILE}")
    print("Tables folder: outputs/tables/")
    print("Figures folder: outputs/figures/")
    print(f"Markdown report: {markdown_path}")
    print(f"DOCX report: {docx_path}")

    print("\nMain results:")
    metrics = results["key_metrics"]
    print(f"- Total revenue: £{metrics['total_revenue']:,.2f}")
    print(f"- Total orders: {metrics['total_orders']:,}")
    print(f"- Unique customers: {metrics['unique_customers']:,}")
    print(f"- Top country: {metrics['top_country']}")
    print(f"- Best revenue month: {metrics['best_month']}")


if __name__ == "__main__":
    main()