import os

import psycopg
from mcp.server.fastmcp import FastMCP
from pglast import ast, parse_sql
from pglast.visitors import Visitor
from psycopg.rows import dict_row

server = FastMCP("simphony-db")
SAFE_FUNCTIONS = {
    "abs", "avg", "count", "date_part", "date_trunc", "extract", "lower",
    "max", "min", "round", "row_number", "string_agg", "sum", "upper",
}


class ReadOnly(Visitor):
    def visit(self, ancestors, node):
        if isinstance(node, ast.SelectStmt):
            if node.intoClause or node.lockingClause:
                raise ValueError("SELECT INTO and row locks are unavailable")
        elif type(node).__name__.endswith("Stmt"):
            raise ValueError("Only SELECT statements are allowed")
        if isinstance(node, ast.FuncCall):
            name = tuple(part.sval for part in node.funcname)
            if len(name) != 2 or name[0] != "pg_catalog" or name[1] not in SAFE_FUNCTIONS:
                raise ValueError("Use an approved pg_catalog function")
        if isinstance(node, ast.RangeVar) and node.schemaname != "mcp_reporting":
            raise ValueError("Use schema-qualified mcp_reporting views")


def validate(query):
    statements = parse_sql(query)
    if len(statements) != 1 or not isinstance(statements[0].stmt, ast.SelectStmt):
        raise ValueError("Provide one SELECT statement")
    ReadOnly()(statements[0].stmt)


def fetch(query):
    with psycopg.connect(os.environ["SIMPHONY_READ_DSN"], connect_timeout=5,
                         row_factory=dict_row) as conn:
        conn.execute("SET TRANSACTION READ ONLY")
        conn.execute("SET LOCAL statement_timeout = '10s'")
        conn.execute("SET LOCAL lock_timeout = '2s'")
        conn.execute("SET LOCAL search_path = pg_catalog")
        flags = conn.execute(
            "SELECT rolsuper, rolcreaterole, rolcreatedb, rolreplication, rolbypassrls "
            "FROM pg_roles WHERE rolname = current_user"
        ).fetchone()
        if not flags or any(flags.values()):
            raise ValueError("Use the dedicated, unprivileged reporting login")
        with conn.cursor(name="report_cursor") as cur:
            cur.execute(query)
            rows = cur.fetchmany(201)
        return {"rows": rows[:200], "truncated": len(rows) > 200}


@server.tool()
def list_reports():
    """List the approved reporting views and their columns."""
    return fetch("SELECT table_name,column_name,data_type FROM information_schema.columns "
                 "WHERE table_schema='mcp_reporting' ORDER BY table_name,ordinal_position")


@server.tool()
def query_reports(sql: str):
    """Query mcp_reporting views with one SELECT. Qualify aggregates, e.g. pg_catalog.sum."""
    if len(sql) > 12000:
        raise ValueError("Query exceeds 12,000 characters")
    validate(sql)
    return fetch(sql)


if __name__ == "__main__":
    server.run(transport="stdio")
