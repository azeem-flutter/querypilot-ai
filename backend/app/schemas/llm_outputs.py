"""Model ke output ka contract. Schema-valid hona sahi SQL hone ki guarantee NAHI hai (Day 5 policy check)."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SQLProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")      # model ne extra field bheji to reject

    status: Literal["ready", "clarify", "unsupported"]
    sql: str | None = Field(default=None, max_length=5000)
    clarification_question: str | None = Field(default=None, max_length=300)
    explanation: str = Field(max_length=500)
    assumptions: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("sql", "clarification_question")
    @classmethod
    def _blank_to_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None

    @model_validator(mode="after")
    def _cross_field_rules(self) -> "SQLProposal":
        if self.status == "ready":
            if not self.sql:
                raise ValueError("status 'ready' requires sql")
            if self.clarification_question:
                raise ValueError("status 'ready' must not contain a clarification_question")
        elif self.status == "clarify":
            if not self.clarification_question:
                raise ValueError("status 'clarify' requires clarification_question")
            if self.sql:
                raise ValueError("status 'clarify' must not contain sql")
        else:  # unsupported
            if self.sql:
                raise ValueError("status 'unsupported' must not contain executable sql")
        return self