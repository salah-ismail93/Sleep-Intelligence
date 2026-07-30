# Sleep Intelligence REST API

Sleep Intelligence is a FastAPI service for sleep-related analysis. It is a
course project in Cloud Architectures and RESTful Services and is aligned with
ongoing PhD research on wearable sleep monitoring.

The project separates deterministic research algorithms from AI integrations:

- `POST /posture` exposes a local deterministic posture-classification
  algorithm based on chest-mounted IMU orientation data.
- `POST /snore` exposes a local Version 1 signal-processing detector.
- `POST /sleep_score` exposes a transparent adult-oriented wellness heuristic
  based on sleep duration and efficiency.
- `POST /chat` uses Ollama as the local AI component.
- `POST /sleep_report` uses Gemini as the remote AI service to generate
  structured, non-diagnostic sleep-wellness reports.

The REST foundation, stateless posture pipeline, Version 1 snore detector, and
sleep-scoring algorithm are implemented, along with the Ollama chat and Gemini
report integrations.

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

## Documentation

- [Project plan](docs/project_plan.md)
- [Architecture](docs/architecture.md)
- [Posture API contract](docs/posture_api_contract.md)
- [Snore API contract](docs/snore_api_contract.md)
- [Sleep-score API contract](docs/sleep_score_api_contract.md)
- [Project TODOs](TODO.md)
