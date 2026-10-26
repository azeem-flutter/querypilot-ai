import pytest
from pydantic import ValidationError

from app.schemas.llm_outputs import SQLProposal

OK = {"explanation": "ok"}


def test_ready_with_sql_is_valid():
    p = SQLProposal(status="ready", sql="SELECT 1", **OK)
    assert p.sql == "SELECT 1" and p.assumptions == []


def test_clarify_with_question_is_valid():
    assert SQLProposal(status="clarify", clarification_question="Which metric?", **OK).sql is None


def test_unsupported_without_sql_is_valid():
    assert SQLProposal(status="unsupported", **OK).sql is None


@pytest.mark.parametrize("data", [
    {"status": "ready", **OK},                                                  # ready ko sql chahiye
    {"status": "ready", "sql": "   ", **OK},                                    # khali sql
    {"status": "ready", "sql": "SELECT 1", "clarification_question": "?", **OK},
    {"status": "clarify", **OK},                                                # clarify ko sawal chahiye
    {"status": "clarify", "clarification_question": "?", "sql": "SELECT 1", **OK},
    {"status": "unsupported", "sql": "DELETE FROM orders", **OK},               # unsupported mein sql nahi
    {"status": "done", "sql": "SELECT 1", **OK},                                # galat status
    {"status": "ready", "sql": "SELECT 1"},                                     # explanation gayab
    {"status": "ready", "sql": "SELECT 1", "explanation": "x" * 501},           # bohot lambi
    {"status": "ready", "sql": "SELECT 1", "explanation": 5},                   # galat type
    {"status": "ready", "sql": "SELECT 1", "extra_field": 1, **OK},             # extra field
])
def test_invalid_shapes_are_rejected(data):
    with pytest.raises(ValidationError):
        SQLProposal(**data)


def test_invalid_json_string_is_rejected():
    with pytest.raises(ValidationError):
        SQLProposal.model_validate_json("this is not json")


def test_valid_sql_string_does_not_mean_correct_sql():
    # Shape ke hisaab se valid hai, lekin sahi nahi: yeh SQL ghalat table use karti hai.
    # Pydantic ise nahi pakadta; yeh Day 5 (SQLGlot + DB role) ka kaam hai.
    p = SQLProposal(status="ready", sql="SELECT * FROM no_such_table", **OK)
    assert p.status == "ready"