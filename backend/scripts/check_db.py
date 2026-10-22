"""Smoke test. backend/ folder se chalao:  python scripts\\check_db.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.connection import check_connection, close_pool, fetch_all  # noqa: E402

info = check_connection()
print("Connected:", info)
assert info["db_user"].startswith("query_readonly"), "Galat role! Restricted credential use karo."
assert info["read_only"] == "on"

for table in ("customers", "categories", "products", "orders", "order_items"):
    n = fetch_all(f"SELECT count(*) AS n FROM {table}")[0]["n"]
    print(f"  {table:12} {n} rows")
close_pool()
print("OK")