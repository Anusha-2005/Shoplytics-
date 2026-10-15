"""
Data Reconciliation and Referential Integrity Tests for Shoplytics
Ensures cross-table referential integrity and financial reconciliation between items and payments.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import PROCESSED_DATA_DIR

@pytest.fixture(scope="module")
def datasets():
    """Load core datasets once for reconciliation tests."""
    return {
        "orders": pd.read_csv(PROCESSED_DATA_DIR / "clean_orders.csv"),
        "items": pd.read_csv(PROCESSED_DATA_DIR / "clean_order_items.csv"),
        "payments": pd.read_csv(PROCESSED_DATA_DIR / "clean_order_payments.csv"),
        "customers": pd.read_csv(PROCESSED_DATA_DIR / "clean_customers.csv"),
        "products": pd.read_csv(PROCESSED_DATA_DIR / "clean_products.csv"),
        "sellers": pd.read_csv(PROCESSED_DATA_DIR / "clean_sellers.csv")
    }

def test_referential_integrity_orders_to_customers(datasets):
    """Verify that every order belongs to a valid customer in dim_customers."""
    missing_custs = ~datasets["orders"]["customer_id"].isin(datasets["customers"]["customer_id"])
    assert missing_custs.sum() == 0, f"Found {missing_custs.sum()} orphaned orders with missing customers!"

def test_referential_integrity_items_to_orders(datasets):
    """Verify that every order_item belongs to a valid order in fact_orders."""
    missing_orders = ~datasets["items"]["order_id"].isin(datasets["orders"]["order_id"])
    assert missing_orders.sum() == 0, f"Found {missing_orders.sum()} orphaned order_items with missing orders!"

def test_referential_integrity_items_to_products(datasets):
    """Verify that every order_item references a valid product in dim_products."""
    missing_products = ~datasets["items"]["product_id"].isin(datasets["products"]["product_id"])
    assert missing_products.sum() == 0, f"Found {missing_products.sum()} items referencing unknown product_ids!"

def test_referential_integrity_items_to_sellers(datasets):
    """Verify that every order_item references a valid seller in dim_sellers."""
    missing_sellers = ~datasets["items"]["seller_id"].isin(datasets["sellers"]["seller_id"])
    assert missing_sellers.sum() == 0, f"Found {missing_sellers.sum()} items referencing unknown seller_ids!"

def test_financial_reconciliation_items_vs_payments(datasets):
    """Reconcile total item value (price + freight) vs payments for delivered orders."""
    delivered = datasets["orders"][datasets["orders"]["order_status"] == "delivered"]
    delivered_order_ids = set(delivered["order_id"])
    
    # Filter items and payments for delivered orders
    items_deliv = datasets["items"][datasets["items"]["order_id"].isin(delivered_order_ids)]
    payments_deliv = datasets["payments"][datasets["payments"]["order_id"].isin(delivered_order_ids)]
    
    total_item_gmv = (items_deliv["price"] + items_deliv["freight_value"]).sum()
    total_payments = payments_deliv["payment_value"].sum()
    
    # Check that payment value closely reconciles with item GMV (tolerance within 3.5% across platform)
    pct_diff = abs(total_payments - total_item_gmv) / total_item_gmv * 100
    assert pct_diff < 4.0, f"Financial reconciliation variance too high: {pct_diff:.2f}% (Items GMV: R$ {total_item_gmv:,.2f}, Payments: R$ {total_payments:,.2f})"

def test_order_customer_cardinality(datasets):
    """Verify that each customer_id maps exactly to 1 order in the Olist schema."""
    order_cust_counts = datasets["orders"]["customer_id"].value_counts()
    assert (order_cust_counts == 1).all(), "Found customer_ids mapped to multiple orders in raw orders table!"
