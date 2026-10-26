import re
from functools import lru_cache
from pathlib import Path

PROMPT_DIR = Path(__file__).parent / "prompts"
_TAGS = re.compile(r"</?\s*(user_question|schema_context)\s*>", re.IGNORECASE)


@lru_cache
def load_prompt(name: str) -> str:
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8").strip()


def render_user_prompt(schema_context: str, question: str) -> str:
    # user delimiter tags nikal do taake woh prompt ka structure tod na sakay (security boundary phir bhi nahi)
    safe_question = _TAGS.sub("", question)
    return (load_prompt("sql_proposal_user")
            .replace("{{SCHEMA_CONTEXT}}", schema_context)
            .replace("{{QUESTION}}", safe_question))