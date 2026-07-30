class OllamaIntegrationError(Exception):
    """Base exception for all Ollama integration failures."""

    pass


class OllamaTimeoutError(OllamaIntegrationError):
    """Raised when a request to Ollama times out."""

    pass


class OllamaConnectionError(OllamaIntegrationError):
    """Raised when network or connection failure prevents reaching Ollama."""

    pass


class OllamaModelNotFoundError(OllamaIntegrationError):
    """Raised when the requested Ollama model is not found (HTTP 404)."""

    pass


class OllamaHTTPError(OllamaIntegrationError):
    """Raised when Ollama returns a non-200 HTTP status code (other than 404)."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"Ollama returned HTTP error status {status_code}.")


class OllamaResponseParseError(OllamaIntegrationError):
    """Raised when Ollama response is not valid JSON or lacks non-empty message.content."""

    pass