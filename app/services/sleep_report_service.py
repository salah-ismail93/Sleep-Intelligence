from typing import Callable, Optional
from pydantic import ValidationError

from app.api.models.sleep_report import SleepReportRequest, SleepReportResponse
from app.config.settings import GeminiSettings, SettingsError, get_gemini_settings
from app.integrations.gemini.client import GeminiClient
from app.integrations.gemini.exceptions import (
    GeminiAuthenticationError,
    GeminiConnectionError,
    GeminiIntegrationError,
    GeminiRateLimitError,
    GeminiResponseParseError,
    GeminiTimeoutError,
)


class SleepReportServiceError(Exception):
    """Base exception for sleep report service failures."""

    pass


class SleepReportServiceTimeoutError(SleepReportServiceError):
    """Raised when the upstream Gemini request times out."""

    pass


class SleepReportServiceUnavailableError(SleepReportServiceError):
    """Raised when Gemini service is unreachable, misconfigured, rate-limited, or unauthorized."""

    pass


class SleepReportServiceUpstreamError(SleepReportServiceError):
    """Raised when Gemini fails to return a valid structured response."""

    pass


def _default_client_factory() -> GeminiClient:
    """Default factory retrieving application settings and instantiating a GeminiClient."""
    settings: GeminiSettings = get_gemini_settings()
    return GeminiClient(settings=settings)


def build_sleep_report_prompt(request: SleepReportRequest) -> str:
    """Constructs a scientifically cautious prompt for Gemini using validated request fields."""
    return (
        f"Generate a sleep quality analysis report based on the following metrics:\n"
        f"- Total Sleep Time: {request.total_sleep_minutes} minutes\n"
        f"- Sleep Efficiency: {request.sleep_efficiency:.2f}\n"
        f"- Sleep Score: {request.sleep_score}\n"
        f"- Snore Events: {request.snore_event_count}\n"
        f"- Posture Changes: {request.posture_change_count}\n\n"
        f"Instructions & Safeguards:\n"
        f"1. Summarize the provided metrics objectively and note key observational limitations.\n"
        f"2. Use cautious, non-causal language such as 'the supplied data shows' or 'may be associated with'. Never claim definitive causation (e.g., 'directly contributed').\n"
        f"3. Treat snore events and posture changes strictly as raw detector outputs, not clinical measurements.\n"
        f"4. Do NOT infer unmeasured parameters such as airway resistance, sleep apnea, breathing quality, sleep architecture/stages, or clinical status.\n"
        f"5. Do NOT label metrics as 'normal', 'healthy', or 'optimal' unless explicit validated reference ranges are provided in the input context.\n"
        f"6. Explicitly acknowledge uncertainty wherever interpretation lacks context, baseline comparisons, or normative reference ranges.\n"
        f"7. Provide general, evidence-based hygiene recommendations aimed at overall sleep wellness.\n"
        f"8. This report is general wellness information only. Do NOT provide medical diagnoses, clinical treatment claims, or fabricate unmeasured metrics.\n"
        f"9. If the supplied data suggests severe disruption or user concern, explicitly advise consulting a qualified healthcare professional."
    )


def generate_sleep_report(
    request: SleepReportRequest,
    client_factory: Optional[Callable[[], GeminiClient]] = None,
) -> SleepReportResponse:
    """Orchestrates Gemini client generation and converts raw dictionary into validated SleepReportResponse."""
    factory = client_factory or _default_client_factory

    try:
        client = factory()
    except SettingsError as exc:
        raise SleepReportServiceUnavailableError(
            "AI generation service is misconfigured."
        ) from exc

    prompt = build_sleep_report_prompt(request)
    json_schema = SleepReportResponse.model_json_schema()

    try:
        raw_data = client.generate_structured_json(
            prompt=prompt,
            response_schema=json_schema,
        )
    except GeminiTimeoutError as exc:
        raise SleepReportServiceTimeoutError("Upstream AI request timed out.") from exc
    except (GeminiAuthenticationError, GeminiRateLimitError, GeminiConnectionError) as exc:
        raise SleepReportServiceUnavailableError(
            "Upstream AI service is currently unavailable or misconfigured."
        ) from exc
    except (GeminiResponseParseError, GeminiIntegrationError) as exc:
        raise SleepReportServiceUpstreamError(
            "Upstream AI service failed to generate a valid report structure."
        ) from exc

    try:
        return SleepReportResponse.model_validate(raw_data)
    except ValidationError as exc:
        raise SleepReportServiceUpstreamError(
            "Upstream AI service output did not conform to the expected schema."
        ) from exc