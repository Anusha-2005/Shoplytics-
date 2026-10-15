"""
Shoplytics SQL Query Runner
Executes analytical SQL queries from sql/queries/ across all analytical domains
and exports the findings to reports/sql_query_insights.md and JSON.
"""

import sys
import json
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import BASE_DIR, REPORTS_DIR
from src.database_loader import get_active_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SQLQueryRunner")

QUERIES_DIR = BASE_DIR / "sql" / "queries"

def parse_sql_file(file_path: Path):
    """Split an SQL file into individual executable statements."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    raw_statements = content.split(";")
    statements = []
    for stmt in raw_statements:
        # Strip comments from each line
        clean_lines = []
        for line in stmt.splitlines():
            stripped = line.strip()
            if not stripped.startswith("--"):
                clean_lines.append(line)
        cleaned_stmt = "\n".join(clean_lines).strip()
        if cleaned_stmt:
            statements.append(cleaned_stmt)
    return statements

def run_all_queries():
    """Execute all SQL queries across all domain files and compile analytical insights."""
    engine, engine_type = get_active_engine()
    logger.info(f"Running analytical SQL queries using engine: {engine_type.upper()}")

    sql_files = sorted(QUERIES_DIR.glob("*.sql"))
    if not sql_files:
        logger.warning(f"No SQL query files found in {QUERIES_DIR}")
        return {}

    all_results = {}
    md_output = [
        "# Shoplytics — SQL Analytics & Business Insights Digest\n",
        f"**Database Engine**: `{engine_type.upper()}`  ",
        "**Generated from**: Production Star Schema Database  \n"
    ]

    with engine.connect() as conn:
        for sql_file in sql_files:
            file_name = sql_file.name
            domain_title = file_name.replace(".sql", "").replace("_", " ").title()
            logger.info(f"Executing domain: {domain_title} ({file_name})")
            
            md_output.append(f"## {domain_title}\n")
            statements = parse_sql_file(sql_file)
            
            all_results[file_name] = []

            for idx, stmt in enumerate(statements, 1):
                try:
                    df = pd.read_sql(text(stmt), conn)
                    records = df.to_dict(orient="records")
                    all_results[file_name].append({
                        "query_index": idx,
                        "rows_returned": len(df),
                        "data": records
                    })
                    
                    md_output.append(f"### Query {idx}\n")
                    md_output.append("```sql")
                    md_output.append(stmt[:300] + ("..." if len(stmt) > 300 else ""))
                    md_output.append("```\n")
                    
                    # Convert dataframe top 10 rows to markdown table
                    if not df.empty:
                        md_table = df.head(10).to_markdown(index=False)
                        md_output.append(md_table + "\n")
                        if len(df) > 10:
                            md_output.append(f"*Showing top 10 of {len(df)} rows*\n")
                    else:
                        md_output.append("*No rows returned.*\n")
                        
                except Exception as e:
                    logger.error(f"Error executing statement {idx} in {file_name}: {e}")
                    md_output.append(f"> **Error**: `{e}`\n")

    # Save output artifacts
    json_path = REPORTS_DIR / "sql_query_insights.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, default=str)
    
    md_path = REPORTS_DIR / "sql_query_insights.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_output))

    logger.info(f"Analytical SQL execution complete! Insights saved to:\n- {md_path}\n- {json_path}")
    return all_results

if __name__ == "__main__":
    run_all_queries()
