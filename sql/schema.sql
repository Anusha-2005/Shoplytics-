-- =============================================================================
-- Shoplytics - E-Commerce Analytics Platform
-- MySQL Database DDL Schema (Star Schema)
-- Designed for high-performance analytical queries and business intelligence
-- =============================================================================

CREATE DATABASE IF NOT EXISTS shoplytics 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE shoplytics;

-- Drop tables in reverse foreign-key order
DROP TABLE IF EXISTS analytics_customer_rfm;
DROP TABLE IF EXISTS fact_order_reviews;
DROP TABLE IF EXISTS fact_order_payments;
DROP TABLE IF EXISTS fact_order_items;
DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS dim_sellers;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_geolocation;

-- -----------------------------------------------------------------------------
-- 1. Dimension: Geolocation (Aggregated by zip code prefix)
-- -----------------------------------------------------------------------------
CREATE TABLE dim_geolocation (
    zip_code_prefix INT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    city VARCHAR(100),
    state CHAR(2),
    PRIMARY KEY (zip_code_prefix),
    INDEX idx_geo_state (state),
    INDEX idx_geo_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 2. Dimension: Customers
-- -----------------------------------------------------------------------------
CREATE TABLE dim_customers (
    customer_id VARCHAR(50) NOT NULL,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state CHAR(2),
    PRIMARY KEY (customer_id),
    INDEX idx_cust_unique (customer_unique_id),
    INDEX idx_cust_state (customer_state),
    INDEX idx_cust_city (customer_city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 3. Dimension: Products
-- -----------------------------------------------------------------------------
CREATE TABLE dim_products (
    product_id VARCHAR(50) NOT NULL,
    product_category_name VARCHAR(100),
    product_category_name_english VARCHAR(100),
    product_category_formatted VARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g FLOAT,
    product_length_cm FLOAT,
    product_height_cm FLOAT,
    product_width_cm FLOAT,
    product_volume_cm3 FLOAT,
    PRIMARY KEY (product_id),
    INDEX idx_prod_cat_en (product_category_name_english),
    INDEX idx_prod_cat_fmt (product_category_formatted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 4. Dimension: Sellers
-- -----------------------------------------------------------------------------
CREATE TABLE dim_sellers (
    seller_id VARCHAR(50) NOT NULL,
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state CHAR(2),
    PRIMARY KEY (seller_id),
    INDEX idx_seller_state (seller_state),
    INDEX idx_seller_city (seller_city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 5. Fact: Orders (Grain: 1 record per order)
-- -----------------------------------------------------------------------------
CREATE TABLE fact_orders (
    order_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_purchase_timestamp DATETIME NOT NULL,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    purchase_year INT,
    purchase_month INT,
    purchase_year_month VARCHAR(7),
    purchase_day_name VARCHAR(15),
    purchase_hour INT,
    actual_delivery_days FLOAT,
    estimated_delivery_days FLOAT,
    delivery_delay_days FLOAT,
    is_delayed TINYINT(1) DEFAULT 0,
    approval_duration_hours FLOAT,
    PRIMARY KEY (order_id),
    INDEX idx_ord_customer (customer_id),
    INDEX idx_ord_status (order_status),
    INDEX idx_ord_purchase_dt (order_purchase_timestamp),
    INDEX idx_ord_ym (purchase_year_month),
    INDEX idx_ord_delayed (is_delayed),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) 
        REFERENCES dim_customers(customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 6. Fact: Order Items (Grain: 1 record per line item)
-- -----------------------------------------------------------------------------
CREATE TABLE fact_order_items (
    order_id VARCHAR(50) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    shipping_limit_date DATETIME,
    price DECIMAL(10, 2) NOT NULL,
    freight_value DECIMAL(10, 2) NOT NULL,
    total_item_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id),
    INDEX idx_item_product (product_id),
    INDEX idx_item_seller (seller_id),
    INDEX idx_item_order (order_id),
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) 
        REFERENCES dim_products(product_id),
    CONSTRAINT fk_items_seller FOREIGN KEY (seller_id) 
        REFERENCES dim_sellers(seller_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 7. Fact: Order Payments (Grain: 1 record per payment tender)
-- -----------------------------------------------------------------------------
CREATE TABLE fact_order_payments (
    order_id VARCHAR(50) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(30) NOT NULL,
    payment_installments INT NOT NULL,
    payment_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential),
    INDEX idx_pay_type (payment_type),
    INDEX idx_pay_order (order_id),
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 8. Fact: Order Reviews (Grain: 1 record per customer review)
-- -----------------------------------------------------------------------------
CREATE TABLE fact_order_reviews (
    review_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    review_score INT NOT NULL,
    review_comment_title TEXT,
    review_comment_message TEXT,
    has_review_comment TINYINT(1) DEFAULT 0,
    review_creation_date DATETIME,
    review_answer_timestamp DATETIME,
    review_response_hours FLOAT,
    sentiment_category VARCHAR(20),
    PRIMARY KEY (review_id, order_id),
    INDEX idx_rev_score (review_score),
    INDEX idx_rev_order (order_id),
    INDEX idx_rev_sentiment (sentiment_category),
    CONSTRAINT fk_reviews_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 9. Analytical Dimension: Customer RFM Segmentation
-- -----------------------------------------------------------------------------
CREATE TABLE analytics_customer_rfm (
    customer_unique_id VARCHAR(50) NOT NULL,
    recency_days INT NOT NULL,
    frequency INT NOT NULL,
    monetary_value DECIMAL(12, 2) NOT NULL,
    state CHAR(2),
    r_score INT NOT NULL,
    f_score INT NOT NULL,
    m_score INT NOT NULL,
    rfm_score VARCHAR(10) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    PRIMARY KEY (customer_unique_id),
    INDEX idx_rfm_seg (customer_segment),
    INDEX idx_rfm_score (rfm_score),
    INDEX idx_rfm_state (state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
