from src.data_loader import download_dataset

if __name__ == "__main__":
    path = download_dataset(force=False)
    print(f"Dataset is ready at: {path}")