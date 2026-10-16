"""
Shoplytics Products & Category Analytics Router
Serves top revenue categories, cumulative Pareto concentration, dimensional freight burden tiers,
and a paginated, searchable product catalog table.
"""

from typing import List, Optional
import math
from fastapi import APIRouter, Query
from src.api.database import execute_query, execute_query_one, build_filter_conditions
from src.api.schemas import (
    CategoryRevenueItem,
    CategoryParetoItem,
    WeightTierItem,
    PaginatedProductsResponse,
    ProductTableItem
)

router = APIRouter(prefix="/products", tags=["Products & Catalog Intelligence"])

@router.get("/top-categories", response_model=List[CategoryRevenueItem])
def get_top_categories(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    limit: int = Query(15, ge=1, le=100)
):
    """Retrieve top product categories ranked by gross merchandise revenue and units sold."""
    clauses, params = build_filter_conditions(start_date, end_date, state, None, "delivered")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    WITH cat_stats AS (
        SELECT 
            p.product_category_formatted AS category,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            COUNT(oi.order_item_id) AS units_sold,
            ROUND(SUM(oi.price), 2) AS total_revenue,
            ROUND(SUM(oi.freight_value), 2) AS total_freight,
            ROUND(AVG(oi.price), 2) AS avg_unit_price
        FROM fact_order_items oi
        JOIN dim_products p ON oi.product_id = p.product_id
        JOIN fact_orders o ON oi.order_id = o.order_id
        JOIN dim_customers c ON o.customer_id = c.customer_id
        {where_sql}
        GROUP BY p.product_category_formatted
        HAVING p.product_category_formatted IS NOT NULL
    ),
    platform_total AS (
        SELECT SUM(total_revenue) AS grand_revenue FROM cat_stats
    )
    SELECT 
        c.category,
        c.total_orders,
        c.units_sold,
        c.total_revenue,
        c.total_freight,
        c.avg_unit_price,
        COALESCE(ROUND((c.total_revenue / NULLIF((SELECT grand_revenue FROM platform_total), 0)) * 100, 2), 0.0) AS revenue_market_share_pct
    FROM cat_stats c
    ORDER BY c.total_revenue DESC
    LIMIT :limit;
    """
    params["limit"] = limit
    rows = execute_query(sql, params)
    return [CategoryRevenueItem(**r) for r in rows]

@router.get("/pareto-analysis", response_model=List[CategoryParetoItem])
def get_pareto_analysis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """Analyze cumulative revenue concentration across catalog categories (80/20 Pareto rule)."""
    clauses, params = build_filter_conditions(start_date, end_date, state, None, "delivered")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    WITH category_revenue AS (
        SELECT 
            p.product_category_formatted AS category,
            ROUND(SUM(oi.price), 2) AS category_revenue
        FROM fact_order_items oi
        JOIN dim_products p ON oi.product_id = p.product_id
        JOIN fact_orders o ON oi.order_id = o.order_id
        JOIN dim_customers c ON o.customer_id = c.customer_id
        {where_sql}
        GROUP BY p.product_category_formatted
        HAVING p.product_category_formatted IS NOT NULL
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
        COALESCE(ROUND((cumulative_revenue / NULLIF(total_platform_revenue, 0)) * 100, 2), 0.0) AS cumulative_percentage
    FROM ranked_categories
    ORDER BY category_revenue DESC
    LIMIT :limit;
    """
    params["limit"] = limit
    rows = execute_query(sql, params)
    return [CategoryParetoItem(**r) for r in rows]

@router.get("/weight-tiers", response_model=List[WeightTierItem])
def get_weight_tiers(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """Evaluate physical weight classes against shipping freight burden and item price ratios."""
    clauses, params = build_filter_conditions(start_date, end_date, state, None, "delivered")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
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
        ROUND(AVG(oi.freight_value / NULLIF(oi.price, 0)) * 100, 2) AS avg_freight_to_price_ratio_pct
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    JOIN fact_orders o ON oi.order_id = o.order_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql}
    GROUP BY weight_tier
    ORDER BY weight_tier;
    """
    rows = execute_query(sql, params)
    return [WeightTierItem(**r) for r in rows]

@router.get("/table", response_model=PaginatedProductsResponse)
def get_product_table(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=5, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by product ID or category"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("total_revenue", pattern="^(total_revenue|units_sold|avg_price|avg_freight|product_weight_g)$"),
    order: str = Query("desc", pattern="^(asc|desc)$")
):
    """Retrieve a searchable, sortable, paginated product catalog performance table."""
    where_parts = []
    params = {}

    if category and category.lower() != "all":
        where_parts.append("p.product_category_formatted = :category")
        params["category"] = category

    if search:
        where_parts.append("(p.product_id LIKE :search OR p.product_category_formatted LIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    # Total unique products matching filter
    count_sql = f"""
    SELECT COUNT(DISTINCT p.product_id) AS total_count
    FROM dim_products p
    JOIN fact_order_items oi ON p.product_id = oi.product_id
    {where_clause};
    """
    count_res = execute_query_one(count_sql, params) or {}
    total_items = count_res.get("total_count", 0)
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    offset = (page - 1) * page_size

    order_dir = "DESC" if order.lower() == "desc" else "ASC"
    sql = f"""
    SELECT 
        p.product_id,
        COALESCE(p.product_category_formatted, 'Uncategorized') AS category,
        COUNT(oi.order_item_id) AS units_sold,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS avg_price,
        ROUND(AVG(oi.freight_value), 2) AS avg_freight,
        p.product_weight_g,
        p.product_volume_cm3
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    {where_clause}
    GROUP BY p.product_id, p.product_category_formatted, p.product_weight_g, p.product_volume_cm3
    ORDER BY {sort_by} {order_dir}
    LIMIT :limit OFFSET :offset;
    """
    params["limit"] = page_size
    params["offset"] = offset

    rows = execute_query(sql, params)
    return PaginatedProductsResponse(
        total_items=total_items,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[ProductTableItem(**r) for r in rows]
    )
