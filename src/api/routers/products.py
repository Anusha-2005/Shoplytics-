"""
Shoplytics Products & Category Analytics Router
Serves top revenue categories, cumulative Pareto concentration, and dimensional freight burden tiers.
"""

from typing import List
from fastapi import APIRouter, Query
from src.api.database import execute_query
from src.api.schemas import (
    CategoryRevenueItem,
    CategoryParetoItem,
    WeightTierItem
)

router = APIRouter(prefix="/products", tags=["Products & Catalog Intelligence"])

@router.get("/top-categories", response_model=List[CategoryRevenueItem])
def get_top_categories(limit: int = Query(15, ge=1, le=100, description="Number of top categories to retrieve")):
    """Retrieve top product categories ranked by gross merchandise revenue and units sold."""
    sql = f"""
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
    LIMIT :limit;
    """
    rows = execute_query(sql, {"limit": limit})
    return [CategoryRevenueItem(**r) for r in rows]

@router.get("/pareto-analysis", response_model=List[CategoryParetoItem])
def get_pareto_analysis(limit: int = Query(20, ge=1, le=100, description="Number of categories to include")):
    """Analyze cumulative revenue concentration across catalog categories (80/20 Pareto rule)."""
    sql = f"""
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
    LIMIT :limit;
    """
    rows = execute_query(sql, {"limit": limit})
    return [CategoryParetoItem(**r) for r in rows]

@router.get("/weight-tiers", response_model=List[WeightTierItem])
def get_weight_tiers():
    """Evaluate physical weight classes against shipping freight burden and item price ratios."""
    sql = """
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
    """
    rows = execute_query(sql)
    return [WeightTierItem(**r) for r in rows]
