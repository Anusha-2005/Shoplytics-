"""
Shoplytics Health & System Router
Provides system liveness, database connectivity status, and table row metrics.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from src.config import DB_ENGINE_TYPE
from src.api.database import execute_query
from src.api.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health & System"])

@router.get("", response_model=HealthResponse)
def check_health():
    """Verify database connectivity and return table row count diagnostics."""
    tables = [
        "fact_orders",
        "fact_order_items",
        "fact_order_payments",
        "fact_order_reviews",
        "dim_customers",
        "dim_products",
        "dim_sellers",
        "dim_geolocation",
        "analytics_customer_rfm"
    ]
    table_counts = {}
    try:
        for tbl in tables:
            res = execute_query(f"SELECT COUNT(*) AS cnt FROM {tbl}")
            table_counts[tbl] = res[0]["cnt"] if res else 0
        
        return HealthResponse(
            status="healthy",
            database_type=DB_ENGINE_TYPE,
            timestamp=datetime.now(timezone.utc).isoformat(),
            table_row_counts=table_counts
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database connectivity check failed: {str(exc)}"
        )
