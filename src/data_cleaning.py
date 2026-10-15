"""
Shoplytics Data Cleaning & Transformation Pipeline
Transforms raw Olist data into high-quality analytical tables.
Never modifies or overwrites the original source files.
"""

import sys
import logging
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DATASET_DIR, PROCESSED_DATA_DIR, DATASET_FILES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DataCleaning")

# Category translations for categories not in the original mapping
ADDITIONAL_TRANSLATIONS = {
    "pc_gamer": "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_food_preparers"
}

def clean_geolocation(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate raw geolocation by zip_code_prefix to prevent Cartesian explosion."""
    logger.info("Cleaning geolocation dataset (aggregating by zip code prefix)...")
    
    # Filter out invalid coordinates (Brazil bounding box approximately lat -35 to 5, lng -75 to -30)
    valid_coords = raw_df[
        (raw_df["geolocation_lat"].between(-35, 6)) & 
        (raw_df["geolocation_lng"].between(-75, -30))
    ]
    
    # Aggregate by zip_code_prefix: mean latitude and longitude, first city & state
    geo_agg = valid_coords.groupby("geolocation_zip_code_prefix").agg({
        "geolocation_lat": "mean",
        "geolocation_lng": "mean",
        "geolocation_city": lambda x: x.mode()[0] if not x.empty else "unknown",
        "geolocation_state": lambda x: x.mode()[0] if not x.empty else "unknown"
    }).reset_index()

    geo_agg.rename(columns={
        "geolocation_zip_code_prefix": "zip_code_prefix",
        "geolocation_lat": "latitude",
        "geolocation_lng": "longitude",
        "geolocation_city": "city",
        "geolocation_state": "state"
    }, inplace=True)
    
    logger.info(f"Clean geolocation produced: {len(geo_agg):,} unique zip code prefixes.")
    return geo_agg

def clean_products(raw_df: pd.DataFrame, translation_df: pd.DataFrame) -> pd.DataFrame:
    """Clean products catalog, merge English translations, impute missing dimensions."""
    logger.info("Cleaning products dataset and mapping English categories...")
    
    df = raw_df.copy()
    
    # Build complete translation map
    trans_map = dict(zip(translation_df["product_category_name"], translation_df["product_category_name_english"]))
    trans_map.update(ADDITIONAL_TRANSLATIONS)
    
    # Map English category
    df["product_category_name_english"] = df["product_category_name"].map(trans_map)
    df["product_category_name_english"] = df["product_category_name_english"].fillna("other_unknown")
    df["product_category_formatted"] = df["product_category_name_english"].str.replace("_", " ").str.title()
    
    # Impute missing physical dimensions using category median, then global median
    numeric_cols = [
        "product_name_lenght", "product_description_lenght", "product_photos_qty",
        "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"
    ]
    for col in numeric_cols:
        df[col] = df.groupby("product_category_name_english")[col].transform(lambda s: s.fillna(s.median()))
        df[col] = df[col].fillna(df[col].median()).fillna(0)

    # Calculate product volume in cm3
    df["product_volume_cm3"] = df["product_length_cm"] * df["product_height_cm"] * df["product_width_cm"]
    
    logger.info(f"Clean products produced: {len(df):,} items.")
    return df

def clean_customers(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean customers table, normalize strings."""
    logger.info("Cleaning customers dataset...")
    df = raw_df.copy()
    df["customer_city"] = df["customer_city"].astype(str).str.strip().str.title()
    df["customer_state"] = df["customer_state"].astype(str).str.strip().str.upper()
    return df

def clean_sellers(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean sellers table, normalize strings."""
    logger.info("Cleaning sellers dataset...")
    df = raw_df.copy()
    df["seller_city"] = df["seller_city"].astype(str).str.strip().str.title()
    df["seller_state"] = df["seller_state"].astype(str).str.strip().str.upper()
    return df

def clean_orders(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean orders table, convert timestamps, compute delivery SLAs and delay flags."""
    logger.info("Cleaning orders dataset and computing delivery metrics...")
    df = raw_df.copy()
    
    # Datetime conversions
    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Time-based analytical dimensions
    purchase_dt = df["order_purchase_timestamp"]
    df["purchase_year"] = purchase_dt.dt.year
    df["purchase_month"] = purchase_dt.dt.month
    df["purchase_year_month"] = purchase_dt.dt.to_period("M").astype(str)
    df["purchase_day_name"] = purchase_dt.dt.day_name()
    df["purchase_hour"] = purchase_dt.dt.hour

    # Delivery performance metrics (in calendar days)
    # Actual delivery duration: purchase to delivered customer
    delivery_delta = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
    df["actual_delivery_days"] = np.where(delivery_delta >= 0, delivery_delta.round(1), np.nan)
    
    # Estimated delivery duration: purchase to estimated delivery
    est_delta = (df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
    df["estimated_delivery_days"] = np.where(est_delta >= 0, est_delta.round(1), np.nan)

    # Delay gap: actual delivered customer date - estimated delivery date (positive = late)
    delay_delta = (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]).dt.total_seconds() / 86400.0
    df["delivery_delay_days"] = delay_delta.round(1)

    # Is delayed flag (1 if delivered after estimated date, 0 otherwise)
    df["is_delayed"] = np.where(
        df["order_delivered_customer_date"].notnull() & 
        (df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]),
        1, 0
    )

    # Order approval duration in hours
    approval_hrs = (df["order_approved_at"] - df["order_purchase_timestamp"]).dt.total_seconds() / 3600.0
    df["approval_duration_hours"] = np.where(approval_hrs >= 0, approval_hrs.round(1), np.nan)

    logger.info(f"Clean orders produced: {len(df):,} records with delivery KPIs.")
    return df

def clean_order_items(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean order items and compute item total value."""
    logger.info("Cleaning order items dataset...")
    df = raw_df.copy()
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")
    df["total_item_value"] = (df["price"] + df["freight_value"]).round(2)
    return df

def clean_order_payments(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean order payments table."""
    logger.info("Cleaning order payments dataset...")
    df = raw_df.copy()
    df["payment_type"] = df["payment_type"].str.replace("_", " ").str.title()
    return df

def clean_order_reviews(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean order reviews, compute response time and sentiment label."""
    logger.info("Cleaning order reviews dataset...")
    df = raw_df.copy()
    
    df["review_creation_date"] = pd.to_datetime(df["review_creation_date"], errors="coerce")
    df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"], errors="coerce")
    
    # Fill comments
    df["review_comment_title"] = df["review_comment_title"].fillna("").astype(str).str.strip()
    df["review_comment_message"] = df["review_comment_message"].fillna("").astype(str).str.strip()
    df["has_review_comment"] = np.where(df["review_comment_message"].str.len() > 0, 1, 0)

    # Response time in hours
    resp_hours = (df["review_answer_timestamp"] - df["review_creation_date"]).dt.total_seconds() / 3600.0
    df["review_response_hours"] = np.where(resp_hours >= 0, resp_hours.round(1), np.nan)

    # Sentiment category based on star rating
    sentiment_conditions = [
        (df["review_score"] >= 4),
        (df["review_score"] == 3),
        (df["review_score"] <= 2)
    ]
    sentiment_labels = ["Positive", "Neutral", "Negative"]
    df["sentiment_category"] = np.select(sentiment_conditions, sentiment_labels, default="Unknown")

    return df

def compute_rfm_segments(orders_df: pd.DataFrame, items_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """Compute RFM (Recency, Frequency, Monetary) segmentation per unique customer."""
    logger.info("Calculating RFM segmentation per unique customer...")
    
    # Filter delivered orders
    delivered = orders_df[orders_df["order_status"] == "delivered"].copy()
    
    # Merge order total items price
    order_values = items_df.groupby("order_id")["price"].sum().reset_index()
    merged = delivered.merge(order_values, on="order_id", how="inner")
    merged = merged.merge(customers_df[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id", how="inner")
    
    # Reference date for recency calculation (max purchase date + 1 day)
    snapshot_date = merged["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    
    rfm = merged.groupby("customer_unique_id").agg({
        "order_purchase_timestamp": lambda dt: (snapshot_date - dt.max()).days,
        "order_id": "nunique",
        "price": "sum",
        "customer_state": "first"
    }).reset_index()
    
    rfm.rename(columns={
        "order_purchase_timestamp": "recency_days",
        "order_id": "frequency",
        "price": "monetary_value",
        "customer_state": "state"
    }, inplace=True)
    
    # RFM Scoring using quantiles with robust rank method for low-frequency ties
    rfm["r_score"] = pd.qcut(rfm["recency_days"], q=4, labels=[4, 3, 2, 1])
    
    # For frequency, most customers purchased once (1), so use rank method
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4])
    rfm["m_score"] = pd.qcut(rfm["monetary_value"].rank(method="first"), q=4, labels=[1, 2, 3, 4])
    
    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)
    
    # Segment assignment
    def assign_segment(row):
        r = int(row["r_score"])
        f = int(row["f_score"])
        m = int(row["m_score"])
        if r >= 3 and f >= 3:
            return "Champions & Loyal"
        elif r >= 3 and f < 3:
            return "Promising Recent"
        elif r == 2 and f >= 2:
            return "Needs Attention"
        elif r == 1 and f >= 3:
            return "At Risk High Value"
        else:
            return "Hibernating / Lost"

    rfm["customer_segment"] = rfm.apply(assign_segment, axis=1)
    logger.info(f"RFM segmentation computed for {len(rfm):,} unique customers.")
    return rfm

def run_cleaning_pipeline():
    """Execute complete end-to-end data cleaning and write processed datasets."""
    logger.info("Starting Shoplytics Data Cleaning & Transformation Pipeline...")
    
    # Read raw datasets
    raw_customers = pd.read_csv(DATASET_DIR / DATASET_FILES["customers"])
    raw_geo = pd.read_csv(DATASET_DIR / DATASET_FILES["geolocation"])
    raw_items = pd.read_csv(DATASET_DIR / DATASET_FILES["order_items"])
    raw_payments = pd.read_csv(DATASET_DIR / DATASET_FILES["order_payments"])
    raw_reviews = pd.read_csv(DATASET_DIR / DATASET_FILES["order_reviews"])
    raw_orders = pd.read_csv(DATASET_DIR / DATASET_FILES["orders"])
    raw_products = pd.read_csv(DATASET_DIR / DATASET_FILES["products"])
    raw_sellers = pd.read_csv(DATASET_DIR / DATASET_FILES["sellers"])
    raw_trans = pd.read_csv(DATASET_DIR / DATASET_FILES["category_translation"])

    # Clean individual tables
    clean_geo_df = clean_geolocation(raw_geo)
    clean_prod_df = clean_products(raw_products, raw_trans)
    clean_cust_df = clean_customers(raw_customers)
    clean_sell_df = clean_sellers(raw_sellers)
    clean_ord_df = clean_orders(raw_orders)
    clean_item_df = clean_order_items(raw_items)
    clean_pay_df = clean_order_payments(raw_payments)
    clean_rev_df = clean_order_reviews(raw_reviews)
    
    # Compute RFM
    rfm_df = compute_rfm_segments(clean_ord_df, clean_item_df, clean_cust_df)

    # Save to processed directory in both CSV and Parquet (if pyarrow/fastparquet available) or CSV
    tables = {
        "clean_customers": clean_cust_df,
        "clean_sellers": clean_sell_df,
        "clean_products": clean_prod_df,
        "clean_geolocation": clean_geo_df,
        "clean_orders": clean_ord_df,
        "clean_order_items": clean_item_df,
        "clean_order_payments": clean_pay_df,
        "clean_order_reviews": clean_rev_df,
        "customer_rfm_segments": rfm_df
    }

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    for name, df in tables.items():
        csv_path = PROCESSED_DATA_DIR / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved {name}.csv ({len(df):,} rows)")

    logger.info("Data cleaning and feature engineering pipeline completed successfully!")
    return tables

if __name__ == "__main__":
    run_cleaning_pipeline()
