"""
Shoplytics Logistics & Delivery SLA Router
Serves carrier SLAs, regional lead times, delay risk factors, and inter-state shipping diagnostics.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from src.api.database import execute_query, execute_query_one
from src.api.schemas import (
    DeliverySLAOverview,
    StateLogisticsItem,
    RouteTypeItem
)

router = APIRouter(prefix="/logistics", tags=["Logistics & Fulfillment"])

@router.get("/overview", response_model=DeliverySLAOverview)
def get_logistics_overview():
    """Retrieve overarching logistics KPIs, SLA breach rates, and delivery durations."""
    sql = """
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
    """
    row = execute_query_one(sql)
    if not row:
        raise HTTPException(status_code=404, detail="No logistics data found.")
    return DeliverySLAOverview(**row)

@router.get("/state-performance", response_model=List[StateLogisticsItem])
def get_state_performance(
    sort_by: str = Query("avg_delivery_days", pattern="^(avg_delivery_days|delivered_orders|state_delay_rate_pct)$"),
    sort_desc: bool = Query(True, description="Sort descending if true")
):
    """Analyze carrier delivery efficiency and delay rates across Brazilian destination states."""
    order_clause = f"{sort_by} {'DESC' if sort_desc else 'ASC'}"
    sql = f"""
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
    ORDER BY {order_clause};
    """
    rows = execute_query(sql)
    return [StateLogisticsItem(**r) for r in rows]

@router.get("/route-comparison", response_model=List[RouteTypeItem])
def get_route_comparison():
    """Compare fulfillment lead times and costs between Intra-State and Inter-State shipments."""
    sql = """
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
    """
    rows = execute_query(sql)
    return [RouteTypeItem(**r) for r in rows]
