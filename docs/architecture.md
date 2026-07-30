# Architecture

## Layered Design

```text
Client
  |
  v
FastAPI routes
  |
  v
Services
  |
  +--> Local algorithms
  |
  +--> External and local-model integrations
  |
  v
Typed JSON response
```

### API Routes and Models

`app/api/` owns HTTP transport concerns:

- Request parsing and validation.
- Response schemas.
- HTTP status codes.
- File-upload handling and limits.
- OpenAPI contracts.

Routes delegate application work to services and do not implement algorithms or
call AI providers directly.

### Services

`app/services/` contains use-case orchestration:

- Convert API models into algorithm or integration inputs.
- Call the appropriate algorithm or integration adapter.
- Convert results into API response models.
- Coordinate multiple components when required.

### Algorithms

`app/algorithms/` contains local deterministic computation and signal
processing. Algorithm modules must not depend on FastAPI, Pydantic, HTTP, cloud
SDKs, file uploads, or API response models.

Version 1 algorithm responsibilities:

- `posture`: relative-quaternion calculation, gravity projection, and stateless
  deterministic posture classification.
- `snore`: local signal processing for validated, uncompressed 16-bit mono PCM
  WAV clips, planned.
- `scoring`: deterministic sleep scoring, planned.

The posture algorithm is the research contribution, but it is not labeled as
the project's local AI component.

### Integrations

`app/integrations/` isolates communication with model runtimes and external
services.

- `ollama/` will provide the local AI adapter used by `POST /chat`.
- `gemini/` will provide the remote AI adapter used by
  `POST /sleep_report`.

Services depend on stable adapter interfaces rather than provider-specific HTTP
or SDK details. Integration failures must be translated into controlled
application errors instead of leaking provider responses or credentials.

## Endpoint-to-Component Mapping

| Endpoint | Service | Algorithm or integration |
| --- | --- | --- |
| `GET /health` | Health route only | None |
| `POST /posture` | Posture service | Local deterministic posture pipeline |
| `POST /snore` | Snore service | Local non-ML signal processing |
| `POST /sleep_score` | Sleep-score service | Local deterministic scoring |
| `POST /sleep_report` | Sleep-report service | Gemini remote AI |
| `POST /chat` | Chat service | Ollama local AI |

## AI Requirement Mapping

- Local AI: Ollama through `POST /chat`.
- Remote AI: Gemini through `POST /sleep_report`.
- Research algorithm: deterministic IMU posture classification through
  `POST /posture`.
- Local non-ML processing: Version 1 snore detection through `POST /snore`.

This terminology is intentional. It avoids presenting deterministic
signal-processing or threshold logic as machine learning.

## State and Configuration

Version 1 endpoints remain stateless. Posture calibration is supplied in each
request, and chat history is not persisted.

Runtime configuration and credentials will be loaded from environment variables.
Ollama model selection, Ollama base URL, Gemini model selection, and Gemini API
credentials must not be hard-coded in routes or services.

## Deferred Capabilities

- Stateful or streaming posture classification.
- Gyroscope-based movement detection.
- Temporal posture smoothing and hysteresis.
- ML-based snore classification.
- Authenticated users and registered wearable devices.
- Persistent calibration and conversation history.
