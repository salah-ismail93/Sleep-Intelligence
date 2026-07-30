class GeminiIntegrationError(Exception):
    """Base exception for all Gemini integration failures."""

    pass


class GeminiTimeoutError(GeminiIntegrationError):
    """Raised when a request to Gemini times out."""

    pass


class GeminiConnectionError(GeminiIntegrationError):
    """Raised when network or connection failures prevent reaching Gemini."""

    pass


class GeminiAuthenticationError(GeminiIntegrationError):
    """Raised when authentication with Gemini fails (e.g., invalid API key)."""

    pass


class GeminiRateLimitError(GeminiIntegrationError):
    """Raised when rate limits or quotas are exceeded on Gemini."""

    pass


class GeminiResponseParseError(GeminiIntegrationError):
    """Raised when Gemini response is invalid JSON, empty, or missing expected content."""

    pass