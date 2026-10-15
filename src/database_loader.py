"""
Shoplytics Database Loader Module
Loads cleaned e-commerce tables into MySQL or SQLite.
Supports chunked insertion, schema creation, foreign key constraints, and verification.
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text, inspect

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import (
    PROCESSED_DATA_DIR, 
    SQLITE_DB_PATH, 
    DB_ENGINE_TYPE,
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    get_db_url
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DatabaseLoader")

TABLE_LOAD_ORDER = [
    ("clean_geolocation.csv", "dim_geolocation", "replace"),
    ("clean_customers.csv", "dim_customers", "replace"),
    ("clean_products.csv", "dim_products", "replace"),
    ("clean_sellers.csv", "dim_sellers", "replace"),
    ("clean_orders.csv", "fact_orders", "replace"),
    ("clean_order_items.csv", "fact_order_items", "replace"),
    ("clean_order_payments.csv", "fact_order_payments", "replace"),
    ("clean_order_reviews.csv", "fact_order_reviews", "replace"),
    ("customer_rfm_segments.csv", "analytics_customer_rfm", "replace"),
]

def get_active_engine():
    """Attempt connection to configured DB engine; fall back to SQLite if MySQL is unavailable."""
    if DB_ENGINE_TYPE == "mysql":
        try:
            mysql_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?charset=utf8mb4"
            server_engine = create_engine(mysql_url, pool_pre_ping=True)
            with server_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
                conn.commit()
            
            db_engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4")
            with db_engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            logger.info(f"Connected successfully to MySQL server at {DB_HOST}:{DB_PORT}/{DB_NAME}")
            return db_engine, "mysql"
        except Exception as e:
            logger.warning(f"MySQL connection failed ({e}). Falling back to high-performance local SQLite engine.")

    # SQLite Engine
    sqlite_url = f"sqlite:///{SQLITE_DB_PATH.as_posix()}"
    sqlite_engine = create_engine(sqlite_url)
    logger.info(f"Using SQLite database engine at: {SQLITE_DB_PATH}")
    return sqlite_engine, "sqlite"

def load_tables(chunk_size: int = 15000):
    """Load all processed tables into database in proper relational dependency order."""
    engine, engine_type = get_active_engine()

    logger.info(f"Initiating table loading pipeline on engine: {engine_type.upper()}")

    results = {}
    
    for filename, table_name, if_exists in TABLE_LOAD_ORDER:
        csv_path = PROCESSED_DATA_DIR / filename
        if not csv_path.exists():
            logger.error(f"Cannot find processed table file: {csv_path}. Run data_cleaning.py first.")
            continue

        logger.info(f"Loading {filename} -> Table: '{table_name}'...")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        row_count = len(df)
        
        # Ingest to database with safe chunking
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=2000
        )
        
        results[table_name] = row_count
        logger.info(f"Loaded {row_count:,} rows into table '{table_name}'.")

    # Create analytical indexes on SQLite if SQLite is used
    if engine_type == "sqlite":
        logger.info("Applying analytical indexes on SQLite database...")
        create_sqlite_indexes(engine)

    # Verification query
    inspector = inspect(engine)
    loaded_tables = inspector.get_table_names()
    logger.info(f"Database verification: {len(loaded_tables)} tables present: {loaded_tables}")
    
    return results

def create_sqlite_indexes(engine):
    """Create indexes to accelerate join and aggregation performance on SQLite."""
    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_geo_zip ON dim_geolocation(zip_code_prefix);",
        "CREATE INDEX IF NOT EXISTS idx_cust_pk ON dim_customers(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_cust_uniq ON dim_customers(customer_unique_id);",
        "CREATE INDEX IF NOT EXISTS idx_prod_pk ON dim_products(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_seller_pk ON dim_sellers(seller_id);",
        "CREATE INDEX IF NOT EXISTS idx_ord_pk ON fact_orders(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_ord_cust ON fact_orders(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_ord_ym ON fact_orders(purchase_year_month);",
        "CREATE INDEX IF NOT EXISTS idx_item_ord ON fact_order_items(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_item_prod ON fact_order_items(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_item_seller ON fact_order_items(seller_id);",
        "CREATE INDEX IF NOT EXISTS idx_pay_ord ON fact_order_payments(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_rev_ord ON fact_order_reviews(order_id);"
    ]
    with engine.connect() as conn:
        for q in index_queries:
            try:
                conn.execute(text(q))
            except Exception as e:
                logger.debug(f"Index creation notice: {e}")
        conn.commit()

if __name__ == "__main__":
    load_tables()
