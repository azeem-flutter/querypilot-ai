"""Asli provider ko aik sawal bhejo.  backend/ se:  python scripts\\try_llm.py "Show the top 5 products by revenue" """
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.llm.provider import get_provider  # noqa: E402
from app.services.query_service import QueryService  # noqa: E402


async def main(question: str) -> None:
    s = get_settings()
    print(f"provider={s.llm_provider} model={s.llm_model or '-'} mode={s.llm_json_mode}")
    proposal = await QueryService(get_provider(s)).propose(question)
    print(proposal.model_dump_json(indent=2))


asyncio.run(main(" ".join(sys.argv[1:]) or "Show the top 5 products by revenue"))