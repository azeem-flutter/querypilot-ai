# ADR-002: Model output is always validated locally with Pydantic

Even when the provider supports JSON-schema mode, we validate the answer ourselves with `SQLProposal`:
- provider support differs per model (some only offer `json_object`), and best-effort modes can still return bad output;
- cross-field rules (ready needs sql, clarify needs a question, unsupported has no sql) are ours, not the provider's;
- schema-valid output is NOT proof of correct or safe SQL. A real run showed it: "pichlay mahine kitni sale hui?" returned valid JSON and valid SQL that counted orders instead of revenue. SQL parsing/policy, result-based evaluation and the read-only DB role (Day 5) stay the real boundary.

Malformed output gets exactly one controlled regeneration (MAX_ATTEMPTS = 2), then a safe error.