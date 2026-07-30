# Final Demonstration Guide

## Goal

Demonstrate the REST architecture, deterministic research components, local AI
through Ollama, remote AI through Gemini, validation, and automated tests in
approximately 7–10 minutes.

## Before the Demonstration

1. Activate the project virtual environment.
2. Confirm that `.env` contains the Gemini API key without displaying it.
3. Confirm that Ollama is running and the configured model is available:

   ```text
   ollama list
   ```

4. Run the automated test suite:

   ```text
   python -m pytest -q
   ```

5. Start the API:

   ```text
   python -m uvicorn app.main:app --reload
   ```

6. Open `http://127.0.0.1:8000/docs`.

Do not open `.env`, display an API key, or add the local WAV examples to Git
during the demonstration.

## Demonstration Sequence

### 1. Health Check

Call `GET /health`.

Expected response:

```json
{
  "status": "healthy"
}
```

Explain that this verifies the FastAPI service is available.

### 2. Stateless IMU Posture Classification

Call `POST /posture` with an identity reference and current quaternion:

```json
{
  "q_reference": {
    "w": 1,
    "x": 0,
    "y": 0,
    "z": 0
  },
  "q_current": {
    "w": 1,
    "x": 0,
    "y": 0,
    "z": 0
  }
}
```

Expected response:

```json
{
  "posture": "supine",
  "confidence": 1
}
```

Explain that calibration is supplied in every request, the algorithm is
stateless, and the quaternion mathematics is independent of FastAPI.

### 3. Local Snore Signal Processing

Call `POST /snore` using the multipart field named `audio`.

First upload the local snore example:

```text
data/audiopapkin-male-snoring-297875_G711.org_.wav
```

Expected decision: `snore_detected: true`.

Then upload either local breathing example:

```text
data/fouziafaraz22-breathing-sound-150861_G711.org_.wav
data/freesound_community-heavy-breathing-14431_G711.org_.wav
```

Expected decision: `snore_detected: false`.

Explain that Version 1 uses deterministic NumPy signal processing, accepts only
validated PCM WAV input, and is neither ML nor clinically validated.

### 4. Transparent Sleep Score

Call `POST /sleep_score`:

```json
{
  "total_sleep_minutes": 420,
  "sleep_efficiency": 0.85,
  "snore_event_count": 2,
  "posture_change_count": 12
}
```

Expected response:

```json
{
  "score": 91
}
```

Explain that the adult-oriented Version 1 heuristic uses duration and
efficiency only. Snore and posture counts remain in the contract for future
research but do not affect the score without validated reference ranges.

### 5. Local AI with Ollama

Call `POST /chat`:

```json
{
  "message": "Give me three concise tips for better sleep hygiene."
}
```

Explain that the response is generated locally by `llama3.2:3b` through
Ollama. The route handles HTTP, the service applies the safety prompt, and the
integration adapter isolates the Ollama API.

Optional safety demonstration:

```json
{
  "message": "Diagnose whether I have sleep apnea from snoring alone."
}
```

The response should avoid diagnosis and recommend professional evaluation.

### 6. Remote AI with Gemini

Call `POST /sleep_report`:

```json
{
  "total_sleep_minutes": 480,
  "sleep_efficiency": 0.85,
  "sleep_score": 88.5,
  "snore_event_count": 2,
  "posture_change_count": 12
}
```

Expected result:

- HTTP `200`
- `summary` is a string
- `insights` is an array of strings
- `recommendations` is an array of strings
- The report avoids diagnosis and unsupported clinical conclusions

Explain that Gemini is the remote AI requirement. The service constrains the
prompt and schema, while the adapter handles the provider SDK and errors.

### 7. Architecture and Tests

Show `docs/architecture.md` and summarize:

```text
Routes -> Services -> Algorithms / Integrations -> Typed responses
```

Show the successful Pytest result. Emphasize that automated tests mock Ollama
and Gemini, so tests do not require live providers or consume API quota.

## Requirement Checklist

| Course requirement | Demonstrated by |
| --- | --- |
| FastAPI REST service | Running API and Swagger UI |
| At least three endpoints | Six implemented endpoints |
| Local AI component | Ollama-backed `/chat` |
| Cloud or remote AI component | Gemini-backed `/sleep_report` |
| Research relevance | IMU posture classification and sleep analysis |
| Public repository | GitHub repository and professional README |

## Closing Statement

Version 1 is a modular research-oriented REST platform, not a complete medical
application. Provider integrations can change without modifying algorithms,
and future research can replace deterministic heuristics while preserving the
service boundaries and API contracts.
