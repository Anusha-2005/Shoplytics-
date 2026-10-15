"""
Shoplytics Configuration Module
Loads environment variables and sets up project paths and database connections.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Dataset path: default to user Downloads if not specified
DEFAULT_DOWNLOADS = Path.home() / "Downloads"
RAW_DATA_PATH_ENV = os.getenv("DATASET_DIR")
if RAW_DATA_PATH_ENV:
    DATASET_DIR = Path(RAW_DATA_PATH_ENV)
else:
    DATASET_DIR = DEFAULT_DOWNLOADS

# Processed data directory
PROCESSED_DATA_DIR = Path(os.getenv("PROCESSED_DATA_DIR", BASE_DIR / "data" / "processed"))
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Reports output directory
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DB_ENGINE_TYPE = os.getenv("DB_ENGINE", "sqlite").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "shoplytics")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

SQLITE_DB_PATH = Path(os.getenv("SQLITE_DB_PATH", BASE_DIR / "data" / "shoplytics.db"))
SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Dataset filenames in Olist Brazilian E-Commerce dataset
DATASET_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

def get_file_path(key: str) -> Path:
    """Return the absolute path to a specific raw dataset file."""
    if key not in DATASET_FILES:
        raise KeyError(f"Unknown dataset key: {key}. Available: {list(DATASET_FILES.keys())}")
    return DATASET_DIR / DATASET_FILES[key]

def get_db_url() -> str:
    """Return SQLAlchemy database connection URL based on configuration."""
    if DB_ENGINE_TYPE == "mysql" and DB_PASSWORD is not None:
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    return f"sqlite:///{SQLITE_DB_PATH.as_posix()}"
