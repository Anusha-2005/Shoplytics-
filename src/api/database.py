"""
Shoplytics API Database Layer
Provides SQLAlchemy engine, connection dependencies, query execution utilities,
and dynamic SQL filter helpers.
"""

from typing import Generator, List, Dict, Any, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from src.config import get_db_url, DB_ENGINE_TYPE

# Brazil geographic region mappings
BRAZIL_REGIONS = {
    "Southeast": ["SP", "RJ", "MG", "ES"],
    "South": ["PR", "SC", "RS"],
    "Northeast": ["BA", "PE", "CE", "MA", "PB", "RN", "AL", "PI", "SE"],
    "Central-West": ["DF", "GO", "MT", "MS"],
    "North": ["AM", "PA", "RO", "TO", "AC", "AP", "RR"]
}
STATE_TO_REGION = {state: reg for reg, states in BRAZIL_REGIONS.items() for state in states}

from sqlalchemy.pool import NullPool

# Create SQLAlchemy engine with connection pooling settings optimized for concurrent analytical requests
if DB_ENGINE_TYPE == "sqlite":
    from sqlalchemy import event
    engine: Engine = create_engine(
        get_db_url(),
        connect_args={"check_same_thread": False, "timeout": 60},
        poolclass=NullPool
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=60000")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
        except Exception:
            pass
else:
    engine: Engine = create_engine(
        get_db_url(),
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=40,
        pool_timeout=60
    )

def get_db() -> Generator[Connection, None, None]:
    """FastAPI dependency to provide an active database connection."""
    with engine.connect() as connection:
        yield connection

def execute_query(sql_query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute a SQL query and return results as a list of dictionaries."""
    with engine.connect() as conn:
        result = conn.execute(text(sql_query), params or {})
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]

def execute_query_one(sql_query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Execute a SQL query and return the first row as a dictionary, or None."""
    results = execute_query(sql_query, params)
    return results[0] if results else None

def build_filter_conditions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    state: Optional[str] = None,
    category: Optional[str] = None,
    order_status: Optional[str] = None,
    date_col: str = "o.order_purchase_timestamp",
    state_col: str = "c.customer_state",
    category_col: str = "p.product_category_formatted",
    status_col: str = "o.order_status"
) -> Tuple[List[str], Dict[str, Any]]:
    """Construct dynamic WHERE clauses and matching bind parameters."""
    clauses = []
    params: Dict[str, Any] = {}

    if start_date:
        clauses.append(f"{date_col} >= :filter_start_date")
        params["filter_start_date"] = f"{start_date} 00:00:00" if len(start_date) == 10 else start_date

    if end_date:
        clauses.append(f"{date_col} <= :filter_end_date")
        params["filter_end_date"] = f"{end_date} 23:59:59" if len(end_date) == 10 else end_date

    if state and state.upper() != "ALL":
        clauses.append(f"{state_col} = :filter_state")
        params["filter_state"] = state.upper()

    if category and category.lower() != "all":
        clauses.append(f"{category_col} = :filter_category")
        params["filter_category"] = category

    if order_status and order_status.lower() != "all":
        clauses.append(f"{status_col} = :filter_status")
        params["filter_status"] = order_status.lower()

    return clauses, params
