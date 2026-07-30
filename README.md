# Sleep Intelligence REST API

Sleep Intelligence is a FastAPI service for sleep-related analysis. It is a
course project in Cloud Architectures and RESTful Services and is aligned with
ongoing PhD research on wearable sleep monitoring.

## Project Status

Version 1 is functional. The REST endpoints, deterministic algorithms, local
Ollama integration, remote Gemini integration, validation, and automated tests
are implemented. Deployment preparation and final hardening remain in progress.

## Architecture

```text
Client
  -> FastAPI routes
  -> Services
  -> Algorithms or integrations
  -> Typed JSON responses
```

Routes own HTTP concerns, services orchestrate use cases, algorithms remain
independent of FastAPI, and integrations isolate Ollama and Gemini SDK details.
See the [architecture document](docs/architecture.md) for the complete design.

## API Endpoints

| Method | Endpoint | Purpose | Component |
| --- | --- | --- | --- |
| `GET` | `/health` | Report API availability | REST platform |
| `POST` | `/posture` | Classify posture from calibrated IMU quaternions | Deterministic local algorithm |
| `POST` | `/snore` | Detect snoring in a validated WAV upload | Deterministic local signal processing |
| `POST` | `/sleep_score` | Calculate an adult-oriented wellness heuristic | Deterministic local algorithm |
| `POST` | `/sleep_report` | Generate a structured sleep-wellness report | Remote Gemini integration |
| `POST` | `/chat` | Answer general sleep-education questions | Local Ollama integration |

Interactive request schemas and examples are available through `/docs` while
the application is running.

## Technology Stack

- FastAPI and Pydantic for the REST API and validation
- NumPy for deterministic audio feature extraction
- Ollama with `llama3.2:3b` for the local AI component
- Google Gemini through the `google-genai` SDK for remote AI reports
- Pytest and FastAPI TestClient for automated testing

## AI Requirement Mapping

- **Local AI:** Ollama powers `POST /chat`.
- **Remote AI:** Gemini powers `POST /sleep_report`.
- **Research component:** The IMU posture pipeline is deterministic and is not
  presented as machine learning.
- **Local signal processing:** The Version 1 snore detector is heuristic,
  non-ML processing.

## Local Setup

### Prerequisites

- Python
- Git
- [Ollama](https://ollama.com/download) for the local `/chat` endpoint
- A Gemini API key for the remote `/sleep_report` endpoint

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Configure the environment

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

Edit the local `.env` and set `GEMINI_API_KEY`. The remaining defaults are:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT_SECONDS=120
GEMINI_MODEL=gemini-3.6-flash
GEMINI_TIMEOUT_SECONDS=120
```

The `.env` file is ignored by Git. Never commit or publish a real API key.

### 4. Prepare Ollama

Install Ollama using its
[official platform instructions](https://ollama.com/download), then download
the configured local model:

```bash
ollama pull llama3.2:3b
```

The Ollama application normally starts its local service on Windows and macOS.
If the service is not already running, start it in a separate terminal:

```bash
ollama serve
```

### 5. Run the API

```bash
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation at
`http://127.0.0.1:8000/docs`.

### 6. Run automated tests

```bash
python -m pytest -q
```

Automated tests mock Ollama and Gemini. They require neither a running Ollama
service nor Gemini API access, and they do not consume remote API quota.

## Testing Strategy

The test suite covers request validation, HTTP status mapping, pure algorithms,
service orchestration, provider failure handling, and secret-safe error
responses. AI integrations are replaced with test doubles in automated tests;
live provider checks are performed separately during manual verification.

## Safety and Research Limitations

- This project provides research-oriented and general wellness services. It is
  not a medical device and does not diagnose or treat sleep disorders.
- Posture classification uses a stateless Version 1 heuristic and requires
  calibrated device orientation.
- Snore detection uses dataset-specific signal-processing thresholds derived
  from a small set of examples and is not clinically validated.
- The sleep score is a transparent adult-oriented wellness heuristic, not a
  clinical score or validated research instrument.
- Snore-event and posture-change counts do not affect Version 1 scoring because
  validated reference ranges are not available.
- Gemini reports and Ollama responses are constrained to general education and
  wellness guidance. Medical concerns should be discussed with a qualified
  healthcare professional.

## Documentation

- [Project plan](docs/project_plan.md)
- [Architecture](docs/architecture.md)
- [Posture API contract](docs/posture_api_contract.md)
- [Snore API contract](docs/snore_api_contract.md)
- [Sleep-score API contract](docs/sleep_score_api_contract.md)
- [Final demonstration guide](docs/demo_guide.md)
- [Project TODOs](TODO.md)

## License

This project is available under the [MIT License](LICENSE).
