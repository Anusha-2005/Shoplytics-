-- =============================================================================
-- Domain 5: Customer Reviews & Satisfaction Diagnostics
-- Shoplytics E-Commerce Analytics Platform
-- =============================================================================

-- Query 5.1: Review Score Distribution & Sentiment Summary
SELECT 
    r.review_score,
    COUNT(r.review_id) AS total_reviews,
    ROUND((COUNT(r.review_id) * 100.0 / (SELECT COUNT(*) FROM fact_order_reviews)), 2) AS pct_of_reviews,
    SUM(r.has_review_comment) AS comments_with_text,
    ROUND(AVG(r.review_response_hours), 1) AS avg_response_hours
FROM fact_order_reviews r
GROUP BY r.review_score
ORDER BY r.review_score DESC;

-- Query 5.2: Delivery Delay Impact on Customer Review Scores (Root Cause Proof)
SELECT 
    CASE 
        WHEN o.is_delayed = 1 THEN 'Delayed Delivery (Past SLA)'
        ELSE 'On-Time / Early Delivery'
    END AS delivery_performance,
    COUNT(r.review_id) AS total_reviews,
    ROUND(AVG(r.review_score), 2) AS average_review_score,
    ROUND((SUM(CASE WHEN r.review_score = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_1_star_reviews,
    ROUND((SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_5_star_reviews
FROM fact_order_reviews r
JOIN fact_orders o ON r.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.is_delayed;

-- Query 5.3: Top 10 Lowest Rated Product Categories (Min 100 Reviews)
SELECT 
    p.product_category_formatted AS category,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.review_score), 2) AS average_score,
    ROUND((SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_negative_reviews,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days
FROM fact_order_reviews r
JOIN fact_orders o ON r.order_id = o.order_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
JOIN dim_products p ON oi.product_id = p.product_id
GROUP BY p.product_category_formatted
HAVING COUNT(r.review_id) >= 100
ORDER BY average_score ASC
LIMIT 10;

-- Query 5.4: Top 10 Highest Rated Product Categories (Min 100 Reviews)
SELECT 
    p.product_category_formatted AS category,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.review_score), 2) AS average_score,
    ROUND((SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_positive_reviews
FROM fact_order_reviews r
JOIN fact_orders o ON r.order_id = o.order_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
JOIN dim_products p ON oi.product_id = p.product_id
GROUP BY p.product_category_formatted
HAVING COUNT(r.review_id) >= 100
ORDER BY average_score DESC
LIMIT 10;
