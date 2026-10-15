-- =============================================================================
-- Domain 4: Logistics & Delivery Performance
-- Shoplytics E-Commerce Analytics Platform
-- =============================================================================

-- Query 4.1: Overall Delivery SLA & On-Time Performance Metrics
SELECT 
    COUNT(order_id) AS total_delivered_orders,
    SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) AS on_time_orders,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_orders,
    ROUND((SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(order_id)), 2) AS on_time_delivery_rate_pct,
    ROUND((SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(order_id)), 2) AS delay_rate_pct,
    ROUND(AVG(actual_delivery_days), 1) AS avg_actual_delivery_days,
    ROUND(AVG(estimated_delivery_days), 1) AS avg_estimated_delivery_days,
    ROUND(AVG(CASE WHEN is_delayed = 1 THEN delivery_delay_days ELSE NULL END), 1) AS avg_days_late_when_delayed
FROM fact_orders
WHERE order_status = 'delivered'
  AND actual_delivery_days IS NOT NULL;

-- Query 4.2: Delivery Efficiency by Customer Destination State
SELECT 
    c.customer_state,
    COUNT(o.order_id) AS delivered_orders,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(o.estimated_delivery_days), 1) AS avg_estimated_days,
    SUM(o.is_delayed) AS delayed_shipments,
    ROUND((SUM(o.is_delayed) * 100.0 / COUNT(o.order_id)), 2) AS state_delay_rate_pct,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_cost
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
  AND o.actual_delivery_days IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC;

-- Query 4.3: Intra-State vs Inter-State Shipping Efficiency
SELECT 
    CASE 
        WHEN c.customer_state = s.seller_state THEN 'Intra-State (Same State)'
        ELSE 'Inter-State (Different State)'
    END AS route_type,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_cost,
    ROUND((SUM(o.is_delayed) * 100.0 / COUNT(DISTINCT o.order_id)), 2) AS delay_rate_pct
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
JOIN dim_sellers s ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
  AND o.actual_delivery_days IS NOT NULL
GROUP BY route_type;
