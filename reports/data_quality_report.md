# Shoplytics — Raw Dataset Quality & Inspection Report

**Dataset Directory**: `C:\Users\anura\Downloads`  
**Audit Status**: Complete  
**Files Inspected**: 9  

## 1. Dataset Files & Record Volume

| File Key | Filename | Size (MB) | Total Rows | Columns | Null Fields Detected |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customers` | `olist_customers_dataset.csv` | 8.62 | 99,441 | 5 | None |
| `geolocation` | `olist_geolocation_dataset.csv` | 58.44 | 1,000,163 | 5 | None |
| `order_items` | `olist_order_items_dataset.csv` | 14.72 | 112,650 | 7 | None |
| `order_payments` | `olist_order_payments_dataset.csv` | 5.51 | 103,886 | 5 | None |
| `order_reviews` | `olist_order_reviews_dataset.csv` | 13.78 | 99,224 | 7 | review_comment_title (87,656), review_comment_message (58,247) |
| `orders` | `olist_orders_dataset.csv` | 16.84 | 99,441 | 8 | order_approved_at (160), order_delivered_carrier_date (1,783), order_delivered_customer_date (2,965) |
| `products` | `olist_products_dataset.csv` | 2.27 | 32,951 | 9 | product_category_name (610), product_name_lenght (610), product_description_lenght (610), product_photos_qty (610), product_weight_g (2), product_length_cm (2), product_height_cm (2), product_width_cm (2) |
| `sellers` | `olist_sellers_dataset.csv` | 0.17 | 3,095 | 4 | None |
| `category_translation` | `product_category_name_translation.csv` | 0.0 | 71 | 2 | None |

## 2. Referential Integrity & Primary Key Checks

| Check Description | Result | Details |
| :--- | :--- | :--- |
| Orders Primary Key Uniqueness | PASSED | 99,441 unique orders |
| Customers Primary Key Uniqueness | PASSED | 96,096 unique customers across orders |
| Orders -> Customers FK Integrity | PASSED | 100% of order customer_ids map to customers |
| Order Items -> Orders FK Integrity | PASSED | 100% of order_items map to valid orders |
| Order Items -> Products FK Integrity | PASSED | 100% of order_items map to valid products |
| Order Items -> Sellers FK Integrity | PASSED | 100% of order_items map to valid sellers |
| Category Translation Coverage | PASSED | 97.26% (2 untranslated: pc_gamer, portateis_cozinha_e_preparadores_de_alimentos) |