# Project Plan

## Goal

Build a maintainable FastAPI platform that exposes sleep-analysis services
related to wearable sleep research while demonstrating both local and remote AI
integration.

## Component Decisions

| Endpoint | Version 1 responsibility | Component type | Status |
| --- | --- | --- | --- |
| `GET /health` | Report API availability | REST platform | Implemented |
| `POST /posture` | Classify posture from calibrated IMU quaternions | Local deterministic research algorithm | Implemented |
| `POST /snore` | Detect snoring in an uploaded WAV file | Local signal processing, non-ML | Implemented |
| `POST /sleep_score` | Calculate a sleep score from validated metrics | Local deterministic algorithm | Implemented |
| `POST /sleep_report` | Generate a structured sleep report | Gemini remote AI service | Implemented |
| `POST /chat` | Answer sleep-related questions | Ollama local AI service | Implemented |

The deterministic posture and snore algorithms are not presented as the
project's local AI component. Ollama is the explicit local AI component, and
Gemini is the explicit remote AI service.

## Delivery Phases

### Phase 1 — Planning and Architecture

Status: Complete.

- Define endpoint responsibilities.
- Establish route, service, algorithm, and integration boundaries.
- Create the repository and package structure.

### Phase 2 — FastAPI Foundation

Status: Complete.

- Create typed request and response models.
- Implement routes and service boundaries.
- Add validation, OpenAPI documentation, and automated endpoint tests.
- Use explicit placeholders for deferred algorithms and integrations.

### Phase 3 — Stateless Posture Classification

Status: Complete.

- Extract quaternion-to-gravity mathematics from the research prototype.
- Implement relative-quaternion composition.
- Implement deterministic single-sample posture regions and confidence.
- Integrate the pure posture pipeline with `POST /posture`.

Temporal hysteresis, movement detection, and majority filtering remain deferred
because they require state, gyroscope data, or streaming input.

### Phase 4 — Version 1 Snore Detection

Status: Complete.

- Enforce the documented PCM WAV input contract.
- Implement a local WAV signal-processing detector.
- Keep audio processing independent of FastAPI.
- Integrate it through the existing snore service.
- Document that Version 1 is non-ML.

### Phase 5 — Ollama Local AI

Status: Implementation complete; local setup documentation pending.

- Add an Ollama integration adapter.
- Configure the local model through environment-based settings.
- Connect the chat service to the adapter.
- Handle unavailable models, timeouts, and malformed responses.
- Test the service with a fake integration rather than requiring Ollama in the
  automated test suite.

### Phase 6 — Gemini Remote AI

Status: Complete.

- Add a Gemini integration adapter.
- Keep credentials outside source control.
- Connect sleep-report generation to Gemini.
- Add timeout, upstream-error, and response-validation handling.
- Mock Gemini in automated tests.

### Phase 7 — Hardening and Delivery

Status: Complete.

- Review API errors, timeouts, and resource limits.
- Complete the professional README and local environment instructions.
- Verify the public repository contains no secrets or research-sensitive data.
- Prepare the course demonstration and architecture documentation.
