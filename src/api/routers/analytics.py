"""
Shoplytics Analytics Router
Serves unified executive KPI summaries and controlled analytical query execution.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from src.api.database import execute_query, execute_query_one
from src.api.schemas import ExecutiveKPISummary

router = APIRouter(prefix="/analytics", tags=["Executive Analytics & Ad-Hoc"])

class CustomQueryRequest(BaseModel):
    query: str = Field(..., description="Read-only SELECT query string")

class CustomQueryResponse(BaseModel):
    row_count: int
    columns: List[str]
    results: List[Dict[str, Any]]

@router.get("/kpi-summary", response_model=ExecutiveKPISummary)
def get_executive_kpis():
    """Retrieve the consolidated executive KPI dashboard summary spanning all 5 analytical domains."""
    # 1. Sales & Financials
    sales_sql = """
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(SUM(oi.freight_value), 2) AS total_freight,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS gmv,
        ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS aov,
        ROUND((SUM(oi.freight_value) / SUM(oi.price)) * 100, 2) AS freight_ratio
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered';
    """
    sales_res = execute_query_one(sales_sql) or {}

    # 2. Logistics SLAs
    logistics_sql = """
    SELECT 
        ROUND((SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(order_id)), 2) AS on_time_rate,
        ROUND(AVG(actual_delivery_days), 1) AS avg_lead_time,
        ROUND(AVG(estimated_delivery_days), 1) AS avg_sla
    FROM fact_orders
    WHERE order_status = 'delivered' AND actual_delivery_days IS NOT NULL;
    """
    logistics_res = execute_query_one(logistics_sql) or {}

    # 3. Reviews & Satisfaction
    reviews_sql = """
    SELECT ROUND(AVG(review_score), 2) AS avg_csat FROM fact_order_reviews;
    """
    reviews_res = execute_query_one(reviews_sql) or {}

    # 4. Repeat purchase loyalty
    repeat_sql = """
    WITH cust_counts AS (
        SELECT customer_unique_id, COUNT(DISTINCT order_id) AS orders
        FROM fact_orders o
        JOIN dim_customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY customer_unique_id
    )
    SELECT 
        ROUND((SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS repeat_rate
    FROM cust_counts;
    """
    repeat_res = execute_query_one(repeat_sql) or {}

    # 5. Top category & payment method
    top_cat_sql = """
    SELECT p.product_category_formatted AS cat, ROUND(SUM(oi.price), 2) AS rev
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    JOIN fact_orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_category_formatted
    ORDER BY rev DESC LIMIT 1;
    """
    top_cat = execute_query_one(top_cat_sql)
    top_cat_str = f"{top_cat['cat']} (R$ {top_cat['rev']:,.2f})" if top_cat else "N/A"

    top_pay_sql = """
    SELECT payment_type, ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_order_payments)), 2) AS pct
    FROM fact_order_payments
    GROUP BY payment_type
    ORDER BY COUNT(*) DESC LIMIT 1;
    """
    top_pay = execute_query_one(top_pay_sql)
    top_pay_str = f"{top_pay['payment_type'].replace('_', ' ').title()} ({top_pay['pct']}%)" if top_pay else "N/A"

    return ExecutiveKPISummary(
        gross_merchandise_value=sales_res.get("gmv", 0.0),
        total_merchandise_revenue=sales_res.get("total_revenue", 0.0),
        total_freight_revenue=sales_res.get("total_freight", 0.0),
        delivered_orders_count=sales_res.get("total_orders", 0),
        average_order_value=sales_res.get("aov", 0.0),
        freight_to_revenue_pct=sales_res.get("freight_ratio", 0.0),
        on_time_delivery_rate_pct=logistics_res.get("on_time_rate", 0.0),
        avg_actual_delivery_lead_time_days=logistics_res.get("avg_lead_time", 0.0),
        avg_estimated_delivery_sla_days=logistics_res.get("avg_sla", 0.0),
        average_customer_satisfaction_rating=reviews_res.get("avg_csat", 0.0),
        repeat_customer_loyalty_rate_pct=repeat_res.get("repeat_rate", 0.0),
        top_payment_method=top_pay_str,
        top_revenue_category=top_cat_str
    )

@router.post("/query", response_model=CustomQueryResponse)
def execute_analytical_query(request: CustomQueryRequest):
    """Execute a validated, read-only SELECT query against the Shoplytics Star Schema database."""
    cleaned = request.query.strip().rstrip(";")
    upper_query = cleaned.upper()

    # Security check: must begin with SELECT or WITH
    if not (upper_query.startswith("SELECT") or upper_query.startswith("WITH")):
        raise HTTPException(
            status_code=400,
            detail="Forbidden query. Only read-only SELECT or CTE (WITH ... SELECT) queries are allowed."
        )

    # Disallow destructive SQL statements
    forbidden_tokens = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "REPLACE", "CREATE", "ATTACH", "DETACH"]
    for token in forbidden_tokens:
        if f" {token} " in f" {upper_query} ":
            raise HTTPException(status_code=400, detail=f"Query rejected: contains forbidden keyword '{token}'.")

    # Enforce safe result limit if not provided
    if "LIMIT" not in upper_query:
        cleaned += " LIMIT 100"

    try:
        rows = execute_query(cleaned)
        cols = list(rows[0].keys()) if rows else []
        return CustomQueryResponse(
            row_count=len(rows),
            columns=cols,
            results=rows
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Query execution error: {str(exc)}")
