-- =============================================================================
-- Domain 3: Customer Segmentation & Demographics
-- Shoplytics E-Commerce Analytics Platform
-- =============================================================================

-- Query 3.1: RFM Customer Segments Breakdown
SELECT 
    customer_segment,
    COUNT(customer_unique_id) AS total_customers,
    ROUND((COUNT(customer_unique_id) * 100.0 / (SELECT COUNT(*) FROM analytics_customer_rfm)), 2) AS pct_of_customers,
    ROUND(SUM(monetary_value), 2) AS segment_total_spend,
    ROUND(AVG(monetary_value), 2) AS avg_monetary_spend,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 2) AS avg_frequency
FROM analytics_customer_rfm
GROUP BY customer_segment
ORDER BY segment_total_spend DESC;

-- Query 3.2: Customer Repeat Purchase Behavior & Loyalty Rate
WITH customer_order_frequencies AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS lifetime_orders,
        SUM(oi.price) AS lifetime_spend
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT 
    CASE 
        WHEN lifetime_orders = 1 THEN '1. One-Time Buyer'
        WHEN lifetime_orders = 2 THEN '2. Repeat Buyer (2 Orders)'
        WHEN lifetime_orders BETWEEN 3 AND 5 THEN '3. Frequent Buyer (3-5 Orders)'
        ELSE '4. Power VIP Buyer (>5 Orders)'
    END AS buyer_cohort,
    COUNT(customer_unique_id) AS customer_count,
    ROUND((COUNT(customer_unique_id) * 100.0 / (SELECT COUNT(*) FROM customer_order_frequencies)), 2) AS pct_customers,
    ROUND(SUM(lifetime_spend), 2) AS cohort_revenue,
    ROUND(AVG(lifetime_spend), 2) AS avg_customer_lifetime_value
FROM customer_order_frequencies
GROUP BY buyer_cohort
ORDER BY buyer_cohort;

-- Query 3.3: Geographic State-Level Performance & Penetration
SELECT 
    c.customer_state,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    COUNT(DISTINCT o.order_id) AS orders_count,
    ROUND(SUM(oi.price), 2) AS state_merchandise_revenue,
    ROUND(AVG(oi.price), 2) AS avg_item_price,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_state_delivery_days
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY state_merchandise_revenue DESC;
