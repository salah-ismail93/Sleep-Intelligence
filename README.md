# Sleep Intelligence REST API

Sleep Intelligence is a FastAPI service for sleep-related analysis. It is a
course project in Cloud Architectures and RESTful Services and is aligned with
ongoing PhD research on wearable sleep monitoring.

The project separates deterministic research algorithms from AI integrations:

- `POST /posture` exposes a local deterministic posture-classification
  algorithm based on chest-mounted IMU orientation data.
- `POST /snore` exposes a local Version 1 signal-processing detector.
- `POST /chat` uses Ollama as the local AI component.
- `POST /sleep_report` uses Gemini as the remote AI service to generate
  structured, non-diagnostic sleep-wellness reports.

The REST foundation, stateless posture pipeline, Version 1 snore detector, and
Ollama chat and Gemini report integrations are implemented. The sleep-scoring
algorithm remains planned work.

## Gemini Configuration

Copy the variable names from `.env.example` into your local `.env` and set the
API key there:

```text
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash
GEMINI_TIMEOUT_SECONDS=120
```

Never commit the real API key. Automated tests mock Gemini and do not make
remote requests or consume API quota.

## Documentation

- [Project plan](docs/project_plan.md)
- [Architecture](docs/architecture.md)
- [Posture API contract](docs/posture_api_contract.md)
- [Snore API contract](docs/snore_api_contract.md)
- [Project TODOs](TODO.md)
