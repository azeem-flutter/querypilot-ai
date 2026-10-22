"""Restricted read-only role ke liye PostgreSQL connection pool.

Har connection khud read-only, time-limited aur approved schema par pinned hai.
Final security boundary phir bhi database ke grants hain (003_restricted_role.sql).
"""
from contextlib import contextmanager
from typing import Any, Iterator

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import Settings, get_settings

_pool: ConnectionPool | None = None


def _configure(conn: Connection) -> None:
    """Har naye pooled connection par aik baar chalta hai."""
    s = get_settings()
    conn.autocommit = True  # session settings open transaction ke andar nahi honi chahiye
    conn.execute(f"SET statement_timeout = {int(s.sql_statement_timeout_ms)}")
    conn.execute("SET search_path = northstar")
    conn.execute("SET default_transaction_read_only = on")
    conn.autocommit = False


def get_pool(settings: Settings | None = None) -> ConnectionPool:
    global _pool
    if _pool is None:
        s = settings or get_settings()
        _pool = ConnectionPool(
            conninfo=s.database_url,
            min_size=s.db_pool_min,
            max_size=s.db_pool_max,
            kwargs={"row_factory": dict_row, "prepare_threshold": None},
            configure=_configure,
            open=True,
        )
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def read_only_cursor() -> Iterator[Any]:
    """READ ONLY transaction ka cursor; hamesha rollback hota hai."""
    with get_pool().connection() as conn:
        conn.read_only = True
        try:
            with conn.cursor() as cur:
                yield cur
        finally:
            conn.rollback()


def fetch_all(sql: str, params: tuple | None = None, max_rows: int | None = None) -> list[dict]:
    """Aik SQL chalao (Day 1: sirf hamari apni queries; generated SQL Day 5 mein)."""
    limit = max_rows or get_settings().sql_max_rows
    with read_only_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchmany(limit)


def check_connection() -> dict:
    rows = fetch_all(
        "SELECT current_user AS db_user, current_setting('search_path') AS search_path, "
        "current_setting('statement_timeout') AS statement_timeout, "
        "current_setting('transaction_read_only') AS read_only"
    )
    return rows[0]