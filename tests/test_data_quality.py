"""
Unit and Quality Tests for Shoplytics Analytical Datasets
Tests file integrity, null constraints, primary key uniqueness, and feature engineering rules.
"""

import os
import sys
from pathlib import Path
import pytest
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DATASET_DIR, DATASET_FILES, PROCESSED_DATA_DIR

def test_raw_dataset_files_exist():
    """Verify all 9 raw dataset files exist in the configured downloads directory."""
    for key, filename in DATASET_FILES.items():
        filepath = DATASET_DIR / filename
        assert filepath.exists(), f"Missing required raw file: {filename} at {filepath}"
        assert os.path.getsize(filepath) > 0, f"Raw file is empty: {filename}"

def test_processed_tables_exist():
    """Verify all cleaned and transformed tables exist in data/processed."""
    expected_tables = [
        "clean_customers.csv",
        "clean_sellers.csv",
        "clean_products.csv",
        "clean_geolocation.csv",
        "clean_orders.csv",
        "clean_order_items.csv",
        "clean_order_payments.csv",
        "clean_order_reviews.csv",
        "customer_rfm_segments.csv"
    ]
    for table_file in expected_tables:
        table_path = PROCESSED_DATA_DIR / table_file
        assert table_path.exists(), f"Processed table not found: {table_file}. Run data_cleaning.py first."
        assert os.path.getsize(table_path) > 0, f"Processed table is empty: {table_file}"

def test_primary_key_uniqueness():
    """Verify primary keys have zero duplicates across core dimension tables."""
    orders_df = pd.read_csv(PROCESSED_DATA_DIR / "clean_orders.csv")
    assert orders_df["order_id"].duplicated().sum() == 0, "Orders table contains duplicate primary keys!"

    cust_df = pd.read_csv(PROCESSED_DATA_DIR / "clean_customers.csv")
    assert cust_df["customer_id"].duplicated().sum() == 0, "Customers table contains duplicate primary keys!"

    prod_df = pd.read_csv(PROCESSED_DATA_DIR / "clean_products.csv")
    assert prod_df["product_id"].duplicated().sum() == 0, "Products table contains duplicate primary keys!"

    seller_df = pd.read_csv(PROCESSED_DATA_DIR / "clean_sellers.csv")
    assert seller_df["seller_id"].duplicated().sum() == 0, "Sellers table contains duplicate primary keys!"

    rfm_df = pd.read_csv(PROCESSED_DATA_DIR / "customer_rfm_segments.csv")
    assert rfm_df["customer_unique_id"].duplicated().sum() == 0, "RFM table contains duplicate customer_unique_ids!"

def test_delivery_delay_flag_logic():
    """Verify that is_delayed is 1 when delivered customer date exceeds estimated delivery date."""
    orders_df = pd.read_csv(PROCESSED_DATA_DIR / "clean_orders.csv")
    delivered = orders_df[orders_df["order_status"] == "delivered"].copy()
    
    # Filter non-null delivered and estimated dates
    delivered_valid = delivered[
        delivered["order_delivered_customer_date"].notnull() & 
        delivered["order_estimated_delivery_date"].notnull()
    ]
    
    expected_delayed = (
        pd.to_datetime(delivered_valid["order_delivered_customer_date"]) > 
        pd.to_datetime(delivered_valid["order_estimated_delivery_date"])
    ).astype(int)
    
    actual_delayed = delivered_valid["is_delayed"].astype(int)
    assert (expected_delayed == actual_delayed).all(), "is_delayed flag logic does not match date comparisons!"

def test_review_score_domain():
    """Verify that all review scores fall in the valid range [1, 5]."""
    reviews_df = pd.read_csv(PROCESSED_DATA_DIR / "clean_order_reviews.csv")
    invalid_scores = reviews_df[~reviews_df["review_score"].between(1, 5)]
    assert len(invalid_scores) == 0, f"Found {len(invalid_scores)} review scores outside the 1-5 range!"
