"""Safe, user-facing LLM errors. Raw provider text kabhi user ko nahi jata."""


class LLMError(Exception):
    code = "llm_error"
    http_status = 502
    public_message = "The AI service failed. Please try again."


class LLMTimeout(LLMError):
    code = "llm_timeout"
    http_status = 504
    public_message = "The AI service took too long to respond. Please try again."


class LLMRateLimited(LLMError):
    code = "llm_rate_limited"
    http_status = 503
    public_message = "The AI service is busy right now. Please try again shortly."


class LLMProviderError(LLMError):
    code = "llm_unavailable"
    http_status = 502
    public_message = "The AI service is currently unavailable."


class LLMMalformedOutput(LLMError):
    code = "llm_bad_output"
    http_status = 502
    public_message = "The AI returned an unusable answer. Please rephrase your question."


class LLMNotConfigured(LLMError):
    code = "llm_not_configured"
    http_status = 503
    public_message = "The AI service is not configured."