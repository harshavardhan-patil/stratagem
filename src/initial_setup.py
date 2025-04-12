from src.data.db import setup_db
from src.data.data_loader import process_case_studies
from src.config import RAW_DATA_DIR

# needs to run once only
if __name__ == "__main__":
    setup_db()
    process_case_studies(RAW_DATA_DIR)
