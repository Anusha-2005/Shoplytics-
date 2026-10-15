-- =============================================================================
-- Domain 2: Product & Category Analytics
-- Shoplytics E-Commerce Analytics Platform
-- =============================================================================

-- Query 2.1: Top 15 Best-Selling Product Categories by Revenue
SELECT 
    p.product_category_formatted AS category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS units_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(SUM(oi.freight_value), 2) AS total_freight,
    ROUND(AVG(oi.price), 2) AS avg_unit_price,
    ROUND((SUM(oi.price) / (SELECT SUM(price) FROM fact_order_items)) * 100, 2) AS revenue_market_share_pct
FROM fact_order_items oi
JOIN dim_products p ON oi.product_id = p.product_id
JOIN fact_orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_formatted
ORDER BY total_revenue DESC
LIMIT 15;

-- Query 2.2: Category Revenue Concentration & Cumulative Pareto Analysis
WITH category_revenue AS (
    SELECT 
        p.product_category_formatted AS category,
        ROUND(SUM(oi.price), 2) AS category_revenue
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    JOIN fact_orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_category_formatted
),
ranked_categories AS (
    SELECT 
        category,
        category_revenue,
        SUM(category_revenue) OVER (ORDER BY category_revenue DESC) AS cumulative_revenue,
        SUM(category_revenue) OVER () AS total_platform_revenue
    FROM category_revenue
)
SELECT 
    category,
    category_revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND((cumulative_revenue / total_platform_revenue) * 100, 2) AS cumulative_percentage
FROM ranked_categories
ORDER BY category_revenue DESC
LIMIT 20;

-- Query 2.3: Physical Weight & Volume Tiers vs Freight Value Impact
SELECT 
    CASE 
        WHEN p.product_weight_g < 500 THEN '1. Light (<0.5 kg)'
        WHEN p.product_weight_g BETWEEN 500 AND 2000 THEN '2. Medium (0.5 - 2 kg)'
        WHEN p.product_weight_g BETWEEN 2001 AND 5000 THEN '3. Heavy (2 - 5 kg)'
        ELSE '4. Bulky (>5 kg)'
    END AS weight_tier,
    COUNT(oi.order_item_id) AS items_shipped,
    ROUND(AVG(oi.price), 2) AS avg_item_price,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_charge,
    ROUND(AVG(oi.freight_value / oi.price) * 100, 2) AS avg_freight_to_price_ratio_pct
FROM fact_order_items oi
JOIN dim_products p ON oi.product_id = p.product_id
GROUP BY weight_tier
ORDER BY weight_tier;
