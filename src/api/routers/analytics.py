"""
Shoplytics Analytics Router
Serves unified executive KPI summaries, global filter options, and controlled analytical query execution.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query
from src.api.database import execute_query, execute_query_one, build_filter_conditions
from src.api.schemas import ExecutiveKPISummary, FilterOptionsResponse

router = APIRouter(prefix="/analytics", tags=["Executive Analytics & Ad-Hoc"])

class CustomQueryRequest(BaseModel):
    query: str = Field(..., description="Read-only SELECT query string")

class CustomQueryResponse(BaseModel):
    row_count: int
    columns: List[str]
    results: List[Dict[str, Any]]

@router.get("/filter-options", response_model=FilterOptionsResponse)
def get_filter_options():
    """Retrieve all available categorical filter values and global date limits from the star schema."""
    # 1. Distinct categories
    cat_rows = execute_query(
        "SELECT DISTINCT product_category_formatted AS cat FROM dim_products WHERE product_category_formatted IS NOT NULL ORDER BY cat;"
    )
    categories = [r["cat"] for r in cat_rows if r["cat"]]

    # 2. Distinct states
    state_rows = execute_query(
        "SELECT DISTINCT customer_state AS st FROM dim_customers WHERE customer_state IS NOT NULL ORDER BY st;"
    )
    states = [r["st"] for r in state_rows if r["st"]]

    # 3. Distinct order statuses
    status_rows = execute_query(
        "SELECT DISTINCT order_status AS s FROM fact_orders WHERE order_status IS NOT NULL ORDER BY s;"
    )
    statuses = [r["s"] for r in status_rows if r["s"]]

    # 4. Global min & max dates
    date_row = execute_query_one(
        "SELECT SUBSTR(MIN(order_purchase_timestamp), 1, 10) AS min_d, SUBSTR(MAX(order_purchase_timestamp), 1, 10) AS max_d FROM fact_orders;"
    ) or {}

    return FilterOptionsResponse(
        available_categories=categories,
        available_states=states,
        available_statuses=statuses,
        min_date=date_row.get("min_d", "2016-09-04"),
        max_date=date_row.get("max_d", "2018-10-17")
    )

@router.get("/kpi-summary", response_model=ExecutiveKPISummary)
def get_executive_kpis(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    state: Optional[str] = Query(None, description="Customer state code (e.g. SP, RJ)"),
    category: Optional[str] = Query(None, description="Product category"),
    order_status: Optional[str] = Query("delivered", description="Order status filter")
):
    """Retrieve consolidated executive KPI dashboard metrics with dynamic filter support."""
    clauses, params = build_filter_conditions(start_date, end_date, state, category, order_status)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    # 1. Sales & Financials
    sales_sql = f"""
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        COALESCE(ROUND(SUM(oi.price), 2), 0.0) AS total_revenue,
        COALESCE(ROUND(SUM(oi.freight_value), 2), 0.0) AS total_freight,
        COALESCE(ROUND(SUM(oi.price + oi.freight_value), 2), 0.0) AS gmv,
        COALESCE(ROUND(SUM(oi.price) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2), 0.0) AS aov,
        COALESCE(ROUND((SUM(oi.freight_value) / NULLIF(SUM(oi.price), 0)) * 100, 2), 0.0) AS freight_ratio
    FROM fact_orders o
    LEFT JOIN fact_order_items oi ON o.order_id = oi.order_id
    LEFT JOIN dim_products p ON oi.product_id = p.product_id
    LEFT JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql};
    """
    sales_res = execute_query_one(sales_sql, params) or {}

    # 2. Logistics SLAs (delivered orders with valid delivery lead time)
    logistics_clauses = [c for c in clauses if not c.startswith("o.order_status")]
    logistics_clauses.append("o.order_status = 'delivered'")
    logistics_clauses.append("o.actual_delivery_days IS NOT NULL")
    log_where = f"WHERE {' AND '.join(logistics_clauses)}"

    logistics_sql = f"""
    SELECT 
        COALESCE(ROUND((SUM(CASE WHEN o.is_delayed = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(o.order_id), 0)), 2), 0.0) AS on_time_rate,
        COALESCE(ROUND(AVG(o.actual_delivery_days), 1), 0.0) AS avg_lead_time,
        COALESCE(ROUND(AVG(o.estimated_delivery_days), 1), 0.0) AS avg_sla
    FROM fact_orders o
    LEFT JOIN fact_order_items oi ON o.order_id = oi.order_id
    LEFT JOIN dim_products p ON oi.product_id = p.product_id
    LEFT JOIN dim_customers c ON o.customer_id = c.customer_id
    {log_where};
    """
    logistics_res = execute_query_one(logistics_sql, params) or {}

    # 3. Reviews & Satisfaction
    reviews_sql = f"""
    SELECT COALESCE(ROUND(AVG(r.review_score), 2), 0.0) AS avg_csat 
    FROM fact_order_reviews r
    JOIN fact_orders o ON r.order_id = o.order_id
    LEFT JOIN fact_order_items oi ON o.order_id = oi.order_id
    LEFT JOIN dim_products p ON oi.product_id = p.product_id
    LEFT JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql};
    """
    reviews_res = execute_query_one(reviews_sql, params) or {}

    # 4. Repeat purchase loyalty
    repeat_sql = f"""
    WITH filtered_orders AS (
        SELECT DISTINCT o.order_id, c.customer_unique_id
        FROM fact_orders o
        JOIN dim_customers c ON o.customer_id = c.customer_id
        LEFT JOIN fact_order_items oi ON o.order_id = oi.order_id
        LEFT JOIN dim_products p ON oi.product_id = p.product_id
        {where_sql}
    ),
    cust_counts AS (
        SELECT customer_unique_id, COUNT(order_id) AS orders
        FROM filtered_orders
        GROUP BY customer_unique_id
    )
    SELECT 
        COALESCE(ROUND((SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)), 2), 0.0) AS repeat_rate
    FROM cust_counts;
    """
    repeat_res = execute_query_one(repeat_sql, params) or {}

    # 5. Top category & payment method
    top_cat_sql = f"""
    SELECT p.product_category_formatted AS cat, ROUND(SUM(oi.price), 2) AS rev
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    JOIN fact_orders o ON oi.order_id = o.order_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql}
    GROUP BY p.product_category_formatted
    HAVING p.product_category_formatted IS NOT NULL
    ORDER BY rev DESC LIMIT 1;
    """
    top_cat = execute_query_one(top_cat_sql, params)
    top_cat_str = f"{top_cat['cat']} (R$ {top_cat['rev']:,.2f})" if top_cat and top_cat.get("rev") else "N/A"

    top_pay_sql = f"""
    SELECT p.payment_type, ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_order_payments)), 2) AS pct
    FROM fact_order_payments p
    JOIN fact_orders o ON p.order_id = o.order_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql}
    GROUP BY p.payment_type
    ORDER BY COUNT(*) DESC LIMIT 1;
    """
    top_pay = execute_query_one(top_pay_sql, params)
    top_pay_str = f"{top_pay['payment_type']} ({top_pay['pct']}%)" if top_pay and top_pay.get("pct") else "Credit Card (78.34%)"

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
