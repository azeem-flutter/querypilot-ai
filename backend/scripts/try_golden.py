"""Golden questions ko model se guzaro aur dekho STATUS (ready/clarify/unsupported) umeed ke mutabiq hai ya nahi.

Yeh sirf behaviour check hai (kab execute, kab clarify, kab refuse). SQL sahi hai ya nahi, yeh Day 5 mein
execution-based evaluation se naapa jayega.

Provider error (timeout, rate limit) ko "galat jawab" nahi ginte: alag ERROR ke taur par dikhate hain.

backend/ se:   python scripts\\try_golden.py            (default 10s delay: Groq free tier ~8000 tokens/min)
               python scripts\\try_golden.py --delay 15
"""
import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.llm.errors import LLMError  # noqa: E402
from app.llm.provider import get_provider  # noqa: E402
from app.services.query_service import QueryService  # noqa: E402

EXPECTED_STATUS = {"execute": "ready", "clarify": "clarify", "unsupported": "unsupported", "refuse": "unsupported"}


async def main(delay: float) -> None:
    s = get_settings()
    service = QueryService(get_provider(s))
    path = ROOT / "evaluation" / "golden_questions.jsonl"
    questions = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    results, match, errors = [], 0, 0
    print(f"provider={s.llm_provider} model={s.llm_model or '-'} mode={s.llm_json_mode} temp={s.llm_temperature}\n")
    for q in questions:
        expected = EXPECTED_STATUS[q["expected_behavior"]]
        t0 = time.perf_counter()
        try:
            p = await service.propose(q["question"])
            got, error = p.status, None
        except LLMError as e:
            got, error = "error", e.code
        ms = int((time.perf_counter() - t0) * 1000)
        ok = got == expected
        match += ok
        errors += got == "error"
        flag = "ok      " if ok else ("ERROR   " if got == "error" else "MISMATCH")
        print(f"{flag} {q['id']:11} expected={expected:11} got={got:11} {ms:5}ms {error or ''}")
        results.append({"id": q["id"], "expected": expected, "got": got, "error": error, "ms": ms})
        await asyncio.sleep(delay)

    print(f"\n{match}/{len(questions)} statuses matched, {errors} provider error(s) "
          f"(dataset size {len(questions)}; behaviour only, SQL not checked)")
    out = ROOT / "evaluation" / "reports" / f"status_check_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps({"provider": s.llm_provider, "model": s.llm_model, "json_mode": s.llm_json_mode,
                               "temperature": s.llm_temperature, "dataset_size": len(questions),
                               "matched": match, "errors": errors, "results": results}, indent=2), encoding="utf-8")
    print(f"saved: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", type=float, default=10.0)
    asyncio.run(main(ap.parse_args().delay))