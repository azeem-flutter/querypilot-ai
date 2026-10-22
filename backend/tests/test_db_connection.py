import psycopg
import pytest

from app.core.config import get_settings


def _db_configured() -> bool:
    try:
        get_settings()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_configured(), reason="DATABASE_URL not configured")

from app.db.connection import check_connection, close_pool, fetch_all  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _pool():
    yield
    close_pool()


def test_connects_as_restricted_role():
    info = check_connection()
    assert info["db_user"].startswith("query_readonly")
    assert info["read_only"] == "on"
    assert info["search_path"] == "northstar"
    assert info["statement_timeout"] in ("3s", "3000ms")


def test_can_read_approved_tables():
    assert fetch_all("SELECT count(*) AS n FROM orders")[0]["n"] > 0


def test_email_column_is_denied():
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        fetch_all("SELECT email FROM customers")


def test_app_metadata_schema_is_denied():
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        fetch_all("SELECT * FROM querypilot.schema_documents")


@pytest.mark.parametrize("sql", [
    "DELETE FROM orders",
    "UPDATE products SET unit_price = 0",
    "INSERT INTO categories(category_name) VALUES ('x')",
    "DROP TABLE orders",
])
def test_writes_are_blocked(sql):
    with pytest.raises((psycopg.errors.InsufficientPrivilege, psycopg.errors.ReadOnlySqlTransaction)):
        fetch_all(sql)


def test_statement_timeout_works():
    with pytest.raises(psycopg.errors.QueryCanceled):
        fetch_all("SELECT pg_sleep(10)")


def test_row_cap_is_applied():
    assert len(fetch_all("SELECT * FROM order_items", max_rows=7)) == 7