"""Har reference_sql ko restricted role se chalao.  backend/ se:  python scripts\\check_golden.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.connection import close_pool, fetch_all  # noqa: E402

path = Path(__file__).resolve().parents[1] / "evaluation" / "golden_questions.jsonl"
ok = bad = 0
for line in path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    q = json.loads(line)
    sql = q.get("reference_sql")
    if not sql:
        print(f"skip {q['id']:11} ({q['expected_behavior']})")
        continue
    try:
        rows = fetch_all(sql)
        first = list(rows[0].values()) if rows else "-"
        print(f"ok   {q['id']:11} {len(rows)} rows, first: {first}")
        ok += 1
    except Exception as e:
        print(f"FAIL {q['id']:11} {e}")
        bad += 1
close_pool()
print(ok, "ok,", bad, "failed")