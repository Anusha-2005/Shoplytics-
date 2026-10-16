"""
Shoplytics Geographic Analysis Router
Serves state and regional level rollup of revenue, order density, customer distribution,
and delivery performance across the 27 Brazilian Federative Units.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from src.api.database import execute_query, build_filter_conditions
from src.api.schemas import GeographicSummaryItem

router = APIRouter(prefix="/geo", tags=["Geographic Analysis"])

@router.get("/summary", response_model=List[GeographicSummaryItem])
def get_geographic_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Retrieve state and macro-region consolidated metrics."""
    clauses, params = build_filter_conditions(start_date, end_date, None, category, "delivered")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    SELECT 
        c.customer_state AS state,
        CASE 
            WHEN c.customer_state IN ('SP', 'RJ', 'MG', 'ES') THEN 'Southeast'
            WHEN c.customer_state IN ('PR', 'SC', 'RS') THEN 'South'
            WHEN c.customer_state IN ('BA', 'PE', 'CE', 'MA', 'PB', 'RN', 'AL', 'PI', 'SE') THEN 'Northeast'
            WHEN c.customer_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Central-West'
            ELSE 'North'
        END AS region,
        COUNT(DISTINCT o.order_id) AS orders_count,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        COALESCE(ROUND(SUM(oi.price), 2), 0.0) AS total_revenue,
        COALESCE(ROUND(SUM(oi.price) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2), 0.0) AS avg_order_value,
        COALESCE(ROUND(AVG(o.actual_delivery_days), 1), 0.0) AS avg_delivery_days,
        COALESCE(ROUND((SUM(o.is_delayed) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0)), 2), 0.0) AS delay_rate_pct,
        COALESCE(ROUND(AVG(oi.freight_value), 2), 0.0) AS avg_freight
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    LEFT JOIN dim_products p ON oi.product_id = p.product_id
    {where_sql}
    GROUP BY c.customer_state
    ORDER BY total_revenue DESC;
    """
    rows = execute_query(sql, params)
    return [GeographicSummaryItem(**r) for r in rows]
