# Shoplytics — SQL Analytics & Business Insights Digest

**Database Engine**: `SQLITE`  
**Generated from**: Production Star Schema Database  

## 01 Sales Performance

### Query 1

```sql
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_order_entities,
    ROUND(SUM(oi.price), 2) AS total_item_revenue,
    ROUND(SUM(oi.freight_value), 2) AS total_freight_revenue,
    ROUND(SUM(oi.total_item_value), 2) AS total_gross_merchandise_value,...
```

|   total_orders |   total_order_entities |   total_item_revenue |   total_freight_revenue |   total_gross_merchandise_value |   average_item_price |   average_order_value_aov |   freight_to_revenue_pct |
|---------------:|-----------------------:|---------------------:|------------------------:|--------------------------------:|---------------------:|--------------------------:|-------------------------:|
|          96478 |                  96478 |          1.32215e+07 |             2.19828e+06 |                     1.54198e+07 |               119.98 |                    137.04 |                    16.63 |

### Query 2

```sql
WITH monthly_metrics AS (
    SELECT 
        o.purchase_year_month,
        COUNT(DISTINCT o.order_id) AS monthly_orders,
        ROUND(SUM(oi.price), 2) AS monthly_revenue,
        ROUND(SUM(oi.freight_value), 2) AS monthly_freight,
        ROUND(AVG(oi.price), 2) AS avg_item_price
    FROM fact_o...
```

| purchase_year_month   |   monthly_orders |   monthly_revenue |   monthly_freight |   prev_month_revenue |   mom_revenue_growth_pct |
|:----------------------|-----------------:|------------------:|------------------:|---------------------:|-------------------------:|
| 2016-09               |                1 |            134.97 |              8.49 |               nan    |            nan           |
| 2016-10               |              265 |          40325.1  |           6165.55 |               134.97 |          29777.1         |
| 2016-12               |                1 |             10.9  |              8.72 |             40325.1  |            -99.97        |
| 2017-01               |              750 |         111798    |          15684    |                10.9  |              1.02557e+06 |
| 2017-02               |             1653 |         234223    |          37015.9  |            111798    |            109.51        |
| 2017-03               |             2546 |         359199    |          55132.1  |            234223    |             53.36        |
| 2017-04               |             2303 |         340670    |          50142.7  |            359199    |             -5.16        |
| 2017-05               |             3546 |         489338    |          77513.1  |            340670    |             43.64        |
| 2017-06               |             3135 |         421923    |          68127    |            489338    |            -13.78        |
| 2017-07               |             3872 |         481605    |          84694.6  |            421923    |             14.15        |

*Showing top 10 of 23 rows*

### Query 3

```sql
SELECT 
    p.payment_type,
    COUNT(DISTINCT p.order_id) AS total_orders,
    ROUND(SUM(p.payment_value), 2) AS total_payment_value,
    ROUND(AVG(p.payment_value), 2) AS average_ticket_size,
    ROUND(AVG(p.payment_installments), 1) AS avg_installments,
    MAX(p.payment_installments) AS max_inst...
```

| payment_type   |   total_orders |   total_payment_value |   average_ticket_size |   avg_installments |   max_installments |   pct_of_total_volume |
|:---------------|---------------:|----------------------:|----------------------:|-------------------:|-------------------:|----------------------:|
| Credit Card    |          76505 |           1.25421e+07 |                163.32 |                3.5 |                 24 |                 78.34 |
| Boleto         |          19784 |           2.86936e+06 |                145.03 |                1   |                  1 |                 17.92 |
| Voucher        |           3866 |      379437           |                 65.7  |                1   |                  1 |                  2.37 |
| Debit Card     |           1528 |      217990           |                142.57 |                1   |                  1 |                  1.36 |
| Not Defined    |              3 |           0           |                  0    |                1   |                  1 |                  0    |

### Query 4

```sql
SELECT 
    o.purchase_day_name,
    o.purchase_hour,
    COUNT(DISTINCT o.order_id) AS orders_count,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM fact_orders o
JOIN fact_order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.purchase_day_name, o.purchase_hour
...
```

| purchase_day_name   |   purchase_hour |   orders_count |   total_revenue |
|:--------------------|----------------:|---------------:|----------------:|
| Tuesday             |              14 |           1095 |          155143 |
| Monday              |              14 |           1063 |          151457 |
| Friday              |              16 |            943 |          150935 |
| Monday              |              21 |           1083 |          150683 |
| Wednesday           |              14 |           1027 |          150342 |
| Wednesday           |              16 |           1008 |          147786 |
| Monday              |              15 |           1047 |          145236 |
| Tuesday             |              16 |           1059 |          145232 |
| Monday              |              11 |           1052 |          144266 |
| Monday              |              22 |            962 |          143613 |

*Showing top 10 of 20 rows*

## 02 Product Analytics

### Query 1

```sql
SELECT 
    p.product_category_formatted AS category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS units_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(SUM(oi.freight_value), 2) AS total_freight,
    ROUND(AVG(oi.price), 2) AS avg_unit_price,
    ROU...
```

| category              |   total_orders |   units_sold |    total_revenue |   total_freight |   avg_unit_price |   revenue_market_share_pct |
|:----------------------|---------------:|-------------:|-----------------:|----------------:|-----------------:|---------------------------:|
| Health Beauty         |           8647 |         9465 |      1.23313e+06 |        178958   |           130.28 |                       9.07 |
| Watches Gifts         |           5495 |         5859 |      1.16618e+06 |         98156.1 |           199.04 |                       8.58 |
| Bed Bath Table        |           9272 |        10953 |      1.02343e+06 |        201774   |            93.44 |                       7.53 |
| Sports Leisure        |           7530 |         8431 | 954853           |        163404   |           113.25 |                       7.03 |
| Computers Accessories |           6530 |         7644 | 888725           |        143999   |           116.26 |                       6.54 |
| Furniture Decor       |           6307 |         8160 | 711928           |        168402   |            87.25 |                       5.24 |
| Housewares            |           5743 |         6795 | 615629           |        142764   |            90.6  |                       4.53 |
| Cool Stuff            |           3559 |         3718 | 610204           |         81476.8 |           164.12 |                       4.49 |
| Auto                  |           3810 |         4140 | 578967           |         90488.1 |           139.85 |                       4.26 |
| Toys                  |           3804 |         4030 | 471286           |         75774.6 |           116.94 |                       3.47 |

*Showing top 10 of 15 rows*

### Query 2

```sql
WITH category_revenue AS (
    SELECT 
        p.product_category_formatted AS category,
        ROUND(SUM(oi.price), 2) AS category_revenue
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    JOIN fact_orders o ON oi.order_id = o.order_id
    WHERE o.order_statu...
```

| category              |   category_revenue |   cumulative_revenue |   cumulative_percentage |
|:----------------------|-------------------:|---------------------:|------------------------:|
| Health Beauty         |        1.23313e+06 |          1.23313e+06 |                    9.33 |
| Watches Gifts         |        1.16618e+06 |          2.39931e+06 |                   18.15 |
| Bed Bath Table        |        1.02343e+06 |          3.42274e+06 |                   25.89 |
| Sports Leisure        |   954853           |          4.3776e+06  |                   33.11 |
| Computers Accessories |   888725           |          5.26632e+06 |                   39.83 |
| Furniture Decor       |   711928           |          5.97825e+06 |                   45.22 |
| Housewares            |   615629           |          6.59388e+06 |                   49.87 |
| Cool Stuff            |   610204           |          7.20408e+06 |                   54.49 |
| Auto                  |   578967           |          7.78305e+06 |                   58.87 |
| Toys                  |   471286           |          8.25433e+06 |                   62.43 |

*Showing top 10 of 20 rows*

### Query 3

```sql
SELECT 
    CASE 
        WHEN p.product_weight_g < 500 THEN '1. Light (<0.5 kg)'
        WHEN p.product_weight_g BETWEEN 500 AND 2000 THEN '2. Medium (0.5 - 2 kg)'
        WHEN p.product_weight_g BETWEEN 2001 AND 5000 THEN '3. Heavy (2 - 5 kg)'
        ELSE '4. Bulky (>5 kg)'
    END AS weight_tier...
```

| weight_tier            |   items_shipped |   avg_item_price |   avg_freight_charge |   avg_freight_to_price_ratio_pct |
|:-----------------------|----------------:|-----------------:|---------------------:|---------------------------------:|
| 1. Light (<0.5 kg)     |           44790 |            75.36 |                15.2  |                            41.92 |
| 2. Medium (0.5 - 2 kg) |           42524 |           112.82 |                17.8  |                            27.07 |
| 3. Heavy (2 - 5 kg)    |           11444 |           180.58 |                22.83 |                            20.7  |
| 4. Bulky (>5 kg)       |           13892 |           241.3  |                39.81 |                            25.12 |

## 03 Customer Segmentation

### Query 1

```sql
SELECT 
    customer_segment,
    COUNT(customer_unique_id) AS total_customers,
    ROUND((COUNT(customer_unique_id) * 100.0 / (SELECT COUNT(*) FROM analytics_customer_rfm)), 2) AS pct_of_customers,
    ROUND(SUM(monetary_value), 2) AS segment_total_spend,
    ROUND(AVG(monetary_value), 2) AS avg_mo...
```

| customer_segment   |   total_customers |   pct_of_customers |   segment_total_spend |   avg_monetary_spend |   avg_recency_days |   avg_frequency |
|:-------------------|------------------:|-------------------:|----------------------:|---------------------:|-------------------:|----------------:|
| Champions & Loyal  |             23491 |              25.16 |           3.45469e+06 |               147.06 |              112.2 |            1.08 |
| Promising Recent   |             23356 |              25.02 |           3.21205e+06 |               137.53 |              112.1 |            1    |
| Hibernating / Lost |             17563 |              18.81 |           2.45314e+06 |               139.68 |              394.1 |            1    |
| Needs Attention    |             17437 |              18.68 |           2.44003e+06 |               139.93 |              277.4 |            1.04 |
| At Risk High Value |             11511 |              12.33 |           1.66158e+06 |               144.35 |              451.9 |            1.05 |

### Query 2

```sql
WITH customer_order_frequencies AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS lifetime_orders,
        SUM(oi.price) AS lifetime_spend
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN fact_order_items oi ON o.order_id = ...
```

| buyer_cohort                   |   customer_count |   pct_customers |   cohort_revenue |   avg_customer_lifetime_value |
|:-------------------------------|-----------------:|----------------:|-----------------:|------------------------------:|
| 1. One-Time Buyer              |            90557 |           97    |      1.24931e+07 |                        137.96 |
| 2. Repeat Buyer (2 Orders)     |             2573 |            2.76 | 631275           |                        245.35 |
| 3. Frequent Buyer (3-5 Orders) |              218 |            0.23 |  90537.7         |                        415.31 |
| 4. Power VIP Buyer (>5 Orders) |               10 |            0.01 |   6596.16        |                        659.62 |

### Query 3

```sql
SELECT 
    c.customer_state,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    COUNT(DISTINCT o.order_id) AS orders_count,
    ROUND(SUM(oi.price), 2) AS state_merchandise_revenue,
    ROUND(AVG(oi.price), 2) AS avg_item_price,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_state_...
```

| customer_state   |   unique_customers |   orders_count |   state_merchandise_revenue |   avg_item_price |   avg_state_delivery_days |
|:-----------------|-------------------:|---------------:|----------------------------:|-----------------:|--------------------------:|
| SP               |              39156 |          40501 |                 5.06763e+06 |           109.1  |                       8.7 |
| RJ               |              11917 |          12350 |                 1.75965e+06 |           124.42 |                      15.1 |
| MG               |              11001 |          11354 |                 1.55248e+06 |           120.2  |                      12   |
| RS               |               5168 |           5345 |            728897           |           118.83 |                      15.2 |
| PR               |               4769 |           4923 |            666064           |           117.91 |                      11.9 |
| SC               |               3449 |           3546 |            507012           |           123.75 |                      15   |
| BA               |               3158 |           3256 |            493584           |           134.02 |                      19.2 |
| DF               |               2019 |           2080 |            296498           |           125.9  |                      13   |
| GO               |               1895 |           1957 |            282837           |           124.21 |                      15.4 |
| ES               |               1928 |           1995 |            268643           |           120.74 |                      15.6 |

*Showing top 10 of 27 rows*

## 04 Delivery Logistics

### Query 1

```sql
SELECT 
    COUNT(order_id) AS total_delivered_orders,
    SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) AS on_time_orders,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_orders,
    ROUND((SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(order_id)), 2) AS on_time_de...
```

|   total_delivered_orders |   on_time_orders |   delayed_orders |   on_time_delivery_rate_pct |   delay_rate_pct |   avg_actual_delivery_days |   avg_estimated_delivery_days |   avg_days_late_when_delayed |
|-------------------------:|-----------------:|-----------------:|----------------------------:|-----------------:|---------------------------:|------------------------------:|-----------------------------:|
|                    96470 |            88644 |             7826 |                       91.89 |             8.11 |                       12.6 |                          23.7 |                          9.6 |

### Query 2

```sql
SELECT 
    c.customer_state,
    COUNT(o.order_id) AS delivered_orders,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(o.estimated_delivery_days), 1) AS avg_estimated_days,
    SUM(o.is_delayed) AS delayed_shipments,
    ROUND((SUM(o.is_delayed) * 100.0 / COUNT(o.orde...
```

| customer_state   |   delivered_orders |   avg_delivery_days |   avg_estimated_days |   delayed_shipments |   state_delay_rate_pct |   avg_freight_cost |
|:-----------------|-------------------:|--------------------:|---------------------:|--------------------:|-----------------------:|-------------------:|
| RR               |                 46 |                28.2 |                 45.8 |                   5 |                  10.87 |              43.09 |
| AP               |                 81 |                28.2 |                 46   |                   4 |                   4.94 |              34.16 |
| AM               |                163 |                26.4 |                 45.6 |                   7 |                   4.29 |              33.31 |
| AL               |                427 |                24.5 |                 32.5 |                 103 |                  24.12 |              35.87 |
| PA               |               1054 |                23.8 |                 37.3 |                 131 |                  12.43 |              35.63 |
| MA               |                800 |                21.6 |                 30.9 |                 163 |                  20.38 |              38.49 |
| SE               |                375 |                21.5 |                 30.8 |                  61 |                  16.27 |              36.57 |
| CE               |               1426 |                21   |                 31.4 |                 218 |                  15.29 |              32.73 |
| AC               |                 91 |                20.7 |                 41   |                   3 |                   3.3  |              40.05 |
| PB               |                586 |                20.6 |                 33   |                  66 |                  11.26 |              43.09 |

*Showing top 10 of 27 rows*

### Query 3

```sql
SELECT 
    CASE 
        WHEN c.customer_state = s.seller_state THEN 'Intra-State (Same State)'
        ELSE 'Inter-State (Different State)'
    END AS route_type,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(oi.freigh...
```

| route_type                    |   total_orders |   avg_delivery_days |   avg_freight_cost |   delay_rate_pct |
|:------------------------------|---------------:|--------------------:|-------------------:|-----------------:|
| Inter-State (Different State) |          61895 |                15   |              23.63 |            10.23 |
| Intra-State (Same State)      |          34822 |                 7.9 |              13.45 |             6.85 |

## 05 Customer Reviews

### Query 1

```sql
SELECT 
    r.review_score,
    COUNT(r.review_id) AS total_reviews,
    ROUND((COUNT(r.review_id) * 100.0 / (SELECT COUNT(*) FROM fact_order_reviews)), 2) AS pct_of_reviews,
    SUM(r.has_review_comment) AS comments_with_text,
    ROUND(AVG(r.review_response_hours), 1) AS avg_response_hours
FROM fa...
```

|   review_score |   total_reviews |   pct_of_reviews |   comments_with_text |   avg_response_hours |
|---------------:|----------------:|-----------------:|---------------------:|---------------------:|
|              5 |           57328 |            57.78 |                20535 |                 77   |
|              4 |           19142 |            19.29 |                 5970 |                 74.9 |
|              3 |            8179 |             8.24 |                 3556 |                 71.5 |
|              2 |            3151 |             3.18 |                 2145 |                 72.1 |
|              1 |           11424 |            11.51 |                 8744 |                 73.2 |

### Query 2

```sql
SELECT 
    CASE 
        WHEN o.is_delayed = 1 THEN 'Delayed Delivery (Past SLA)'
        ELSE 'On-Time / Early Delivery'
    END AS delivery_performance,
    COUNT(r.review_id) AS total_reviews,
    ROUND(AVG(r.review_score), 2) AS average_review_score,
    ROUND((SUM(CASE WHEN r.review_score = 1 ...
```

| delivery_performance        |   total_reviews |   average_review_score |   pct_1_star_reviews |   pct_5_star_reviews |
|:----------------------------|----------------:|-----------------------:|---------------------:|---------------------:|
| On-Time / Early Delivery    |           88661 |                   4.29 |                 6.6  |                62.43 |
| Delayed Delivery (Past SLA) |            7700 |                   2.57 |                46.16 |                22.22 |

### Query 3

```sql
SELECT 
    p.product_category_formatted AS category,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.review_score), 2) AS average_score,
    ROUND((SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_negative_reviews,
    ROUND(AVG(o.actual_delivery...
```

| category                  |   review_count |   average_score |   pct_negative_reviews |   avg_delivery_days |
|:--------------------------|---------------:|----------------:|-----------------------:|--------------------:|
| Office Furniture          |           1687 |            3.49 |                  26.08 |                20.8 |
| Fashion Male Clothing     |            131 |            3.64 |                  28.24 |                12.8 |
| Fixed Telephony           |            262 |            3.68 |                  25.57 |                12.6 |
| Audio                     |            361 |            3.83 |                  21.88 |                13.3 |
| Home Confort              |            435 |            3.83 |                  20.23 |                13.5 |
| Construction Tools Safety |            193 |            3.84 |                  20.21 |                11.9 |
| Other Unknown             |           1598 |            3.84 |                  22.09 |                12.8 |
| Bed Bath Table            |          11137 |            3.9  |                  18.96 |                12.8 |
| Furniture Decor           |           8331 |            3.9  |                  19.46 |                12.8 |
| Furniture Living Room     |            502 |            3.9  |                  18.13 |                13.8 |

### Query 4

```sql
SELECT 
    p.product_category_formatted AS category,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.review_score), 2) AS average_score,
    ROUND((SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_positive_reviews
FROM fact_order_reviews r
JOIN f...
```

| category               |   review_count |   average_score |   pct_positive_reviews |
|:-----------------------|---------------:|----------------:|-----------------------:|
| Books General Interest |            549 |            4.45 |                  87.8  |
| Books Technical        |            266 |            4.37 |                  85.34 |
| Luggage Accessories    |           1088 |            4.32 |                  83.73 |
| Food Drink             |            279 |            4.32 |                  81.72 |
| Fashion Shoes          |            261 |            4.23 |                  80.84 |
| Food                   |            495 |            4.22 |                  81.82 |
| Stationery             |           2507 |            4.19 |                  80.73 |
| Pet Shop               |           1939 |            4.19 |                  79.68 |
| Computers              |            200 |            4.18 |                  81.5  |
| Home Appliances        |            806 |            4.17 |                  79.9  |
