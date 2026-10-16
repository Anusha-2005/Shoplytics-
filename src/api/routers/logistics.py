"""
Shoplytics Logistics & Delivery SLA Router
Serves carrier SLAs, regional lead times, delay risk factors, macro-region rollups,
and inter-state shipping diagnostics.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from src.api.database import execute_query, execute_query_one, build_filter_conditions
from src.api.schemas import (
    DeliverySLAOverview,
    StateLogisticsItem,
    RegionalLogisticsItem,
    RouteTypeItem
)

router = APIRouter(prefix="/logistics", tags=["Logistics & Fulfillment"])

@router.get("/overview", response_model=DeliverySLAOverview)
def get_logistics_overview(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Retrieve overarching logistics KPIs, SLA breach rates, and delivery durations with deduplicated order joins."""
    clauses, params = build_filter_conditions(start_date, end_date, state, category, "delivered")
    clauses.append("o.actual_delivery_days IS NOT NULL")
    where_sql = f"WHERE {' AND '.join(clauses)}"

    sql = f"""
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_delivered_orders,
        COUNT(DISTINCT CASE WHEN o.is_delayed = 0 THEN o.order_id END) AS on_time_orders,
        COUNT(DISTINCT CASE WHEN o.is_delayed = 1 THEN o.order_id END) AS delayed_orders,
        COALESCE(ROUND((COUNT(DISTINCT CASE WHEN o.is_delayed = 0 THEN o.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0)), 2), 0.0) AS on_time_delivery_rate_pct,
        COALESCE(ROUND((COUNT(DISTINCT CASE WHEN o.is_delayed = 1 THEN o.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0)), 2), 0.0) AS delay_rate_pct,
        COALESCE(ROUND(AVG(o.actual_delivery_days), 1), 0.0) AS avg_actual_delivery_days,
        COALESCE(ROUND(AVG(o.estimated_delivery_days), 1), 0.0) AS avg_estimated_delivery_days,
        COALESCE(ROUND(AVG(CASE WHEN o.is_delayed = 1 THEN o.delivery_delay_days ELSE NULL END), 1), 0.0) AS avg_days_late_when_delayed
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    LEFT JOIN fact_order_items oi ON o.order_id = oi.order_id
    LEFT JOIN dim_products p ON oi.product_id = p.product_id
    {where_sql};
    """
    row = execute_query_one(sql, params)
    if not row or row.get("total_delivered_orders", 0) == 0:
        return DeliverySLAOverview(
            total_delivered_orders=0,
            on_time_orders=0,
            delayed_orders=0,
            on_time_delivery_rate_pct=0.0,
            delay_rate_pct=0.0,
            avg_actual_delivery_days=0.0,
            avg_estimated_delivery_days=0.0,
            avg_days_late_when_delayed=0.0
        )
    return DeliverySLAOverview(**row)

@router.get("/state-performance", response_model=List[StateLogisticsItem])
def get_state_performance(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: str = Query("avg_delivery_days", pattern="^(avg_delivery_days|delivered_orders|state_delay_rate_pct)$"),
    sort_desc: bool = Query(True)
):
    """Analyze carrier delivery efficiency and delay rates across Brazilian destination states."""
    clauses, params = build_filter_conditions(start_date, end_date, None, category, "delivered")
    clauses.append("o.actual_delivery_days IS NOT NULL")
    where_sql = f"WHERE {' AND '.join(clauses)}"
    order_clause = f"{sort_by} {'DESC' if sort_desc else 'ASC'}"

    sql = f"""
    SELECT 
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS delivered_orders,
        ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days,
        ROUND(AVG(o.estimated_delivery_days), 1) AS avg_estimated_days,
        COUNT(DISTINCT CASE WHEN o.is_delayed = 1 THEN o.order_id END) AS delayed_shipments,
        ROUND((COUNT(DISTINCT CASE WHEN o.is_delayed = 1 THEN o.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0)), 2) AS state_delay_rate_pct,
        ROUND(AVG(oi.freight_value), 2) AS avg_freight_cost
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    LEFT JOIN dim_products p ON oi.product_id = p.product_id
    {where_sql}
    GROUP BY c.customer_state
    ORDER BY {order_clause};
    """
    rows = execute_query(sql, params)
    return [StateLogisticsItem(**r) for r in rows]

@router.get("/regional-performance", response_model=List[RegionalLogisticsItem])
def get_regional_performance(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Aggregate logistics performance by official Brazilian geographic macro-regions."""
    clauses, params = build_filter_conditions(start_date, end_date, None, None, "delivered")
    clauses.append("o.actual_delivery_days IS NOT NULL")
    where_sql = f"WHERE {' AND '.join(clauses)}"

    sql = f"""
    SELECT 
        CASE 
            WHEN c.customer_state IN ('SP', 'RJ', 'MG', 'ES') THEN 'Southeast'
            WHEN c.customer_state IN ('PR', 'SC', 'RS') THEN 'South'
            WHEN c.customer_state IN ('BA', 'PE', 'CE', 'MA', 'PB', 'RN', 'AL', 'PI', 'SE') THEN 'Northeast'
            WHEN c.customer_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Central-West'
            ELSE 'North'
        END AS region,
        COUNT(DISTINCT c.customer_state) AS state_count,
        COUNT(DISTINCT o.order_id) AS delivered_orders,
        ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days,
        ROUND(AVG(o.estimated_delivery_days), 1) AS avg_estimated_days,
        ROUND((COUNT(DISTINCT CASE WHEN o.is_delayed = 1 THEN o.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0)), 2) AS delay_rate_pct,
        ROUND(AVG(oi.freight_value), 2) AS avg_freight_cost
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    {where_sql}
    GROUP BY region
    ORDER BY delivered_orders DESC;
    """
    rows = execute_query(sql, params)
    return [RegionalLogisticsItem(**r) for r in rows]

@router.get("/route-comparison", response_model=List[RouteTypeItem])
def get_route_comparison(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Compare fulfillment lead times and costs between Intra-State and Inter-State shipments."""
    clauses, params = build_filter_conditions(start_date, end_date, None, None, "delivered")
    clauses.append("o.actual_delivery_days IS NOT NULL")
    where_sql = f"WHERE {' AND '.join(clauses)}"

    sql = f"""
    SELECT 
        CASE 
            WHEN c.customer_state = s.seller_state THEN 'Intra-State (Same State)'
            ELSE 'Inter-State (Different State)'
        END AS route_type,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days,
        ROUND(AVG(oi.freight_value), 2) AS avg_freight_cost,
        ROUND((COUNT(DISTINCT CASE WHEN o.is_delayed = 1 THEN o.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT o.order_id), 0)), 2) AS delay_rate_pct
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    JOIN dim_sellers s ON oi.seller_id = s.seller_id
    {where_sql}
    GROUP BY route_type;
    """
    rows = execute_query(sql, params)
    return [RouteTypeItem(**r) for r in rows]
