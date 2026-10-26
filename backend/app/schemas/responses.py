from typing import Literal

from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    request_id: str
    status: Literal["ready", "clarify", "unsupported"]
    question: str
    sql: str | None = None
    clarification_question: str | None = None
    explanation: str
    assumptions: list[str] = Field(default_factory=list)
    executed: bool = False        # Day 2: SQL sirf propose hoti hai, chalti nahi (execution Day 5)
    duration_ms: int


class ErrorResponse(BaseModel):
    request_id: str
    error_code: str
    message: str