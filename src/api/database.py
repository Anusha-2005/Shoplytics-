"""
Shoplytics API Database Layer
Provides SQLAlchemy engine, connection dependencies, and query execution utilities.
"""

from typing import Generator, List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from src.config import get_db_url, DB_ENGINE_TYPE

# Create SQLAlchemy engine with connection pooling settings
_connect_args = {"check_same_thread": False} if DB_ENGINE_TYPE == "sqlite" else {}
engine: Engine = create_engine(
    get_db_url(),
    pool_pre_ping=True,
    connect_args=_connect_args
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
