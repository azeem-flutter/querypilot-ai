import logging

from pydantic import ValidationError

from app.llm.errors import LLMMalformedOutput
from app.llm.prompt_loader import load_prompt, render_user_prompt
from app.llm.provider import LLMProvider
from app.schemas.llm_outputs import SQLProposal
from app.services.static_schema import STATIC_SCHEMA_CONTEXT

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2  # pehli koshish + sirf ek controlled regeneration (bounded)


class QueryService:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def propose(self, question: str) -> SQLProposal:
        system = load_prompt("sql_proposal_system")
        user = render_user_prompt(STATIC_SCHEMA_CONTEXT, question)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            raw = await self.provider.generate(system, user)
            try:
                return SQLProposal.model_validate_json(raw)   # JSON parse + schema + cross-field, aik jagah
            except ValidationError as e:
                # sirf error ki tafseel (field/type) log karo, model ka raw output nahi
                logger.warning("invalid model output (attempt %d/%d): %d error(s) %s",
                               attempt, MAX_ATTEMPTS, e.error_count(),
                               [err["type"] for err in e.errors()][:3])
        raise LLMMalformedOutput()