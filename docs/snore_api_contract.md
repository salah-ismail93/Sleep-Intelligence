# Snore API Contract

## Endpoint

`POST /snore`

Version 1 accepts one audio clip and applies a local, deterministic
signal-processing detector. The detector is non-ML and is not the project's
local AI component.

## Request Transport

The request uses `multipart/form-data` with one required file field named
`audio`.

The uploaded filename must end with `.wav`, using a case-insensitive check. The
service must inspect the WAV container; a filename or declared MIME type alone
is not sufficient evidence that the content is valid WAV audio.

The maximum upload size is exactly 10 MiB:

`10 × 1024 × 1024 = 10,485,760 bytes`

The service must use a bounded read and must not load data beyond the size
limit into memory.

## Supported WAV Properties

Version 1 accepts audio only when all of the following are true:

- Container: valid RIFF/WAVE.
- Encoding: uncompressed linear PCM.
- Sample width: exactly 16 bits, or 2 bytes, per sample.
- Channels: exactly 1 (mono).
- Sample rate: from 8,000 to 48,000 Hz inclusive.
- Duration: from 0.5 to 30.0 seconds inclusive.

Duration is calculated from decoded WAV metadata:

`duration_seconds = frame_count / sample_rate`

Both duration boundaries are accepted. Floating-point comparisons must use the
duration derived from the integer frame count and sample rate; clients do not
supply duration metadata separately.

Version 1 must not:

- Resample audio.
- Downmix stereo or multichannel audio.
- Convert sample widths.
- Decode or transcode compressed audio.
- Repair malformed or truncated WAV files.

## Validation Rules and Errors

Validation occurs before signal processing. The detector must not run when any
validation rule fails.

| Condition | HTTP status | Required behavior |
| --- | --- | --- |
| Missing `audio` form field | `422 Unprocessable Content` | Use FastAPI request-validation response |
| Filename missing or extension is not `.wav` | `415 Unsupported Media Type` | Reject before WAV decoding |
| Upload exceeds 10,485,760 bytes | `413 Content Too Large` | Stop after the bounded size check |
| Content is not a RIFF/WAVE container | `415 Unsupported Media Type` | Reject content that is not WAV |
| WAV uses compressed or unsupported encoding | `415 Unsupported Media Type` | Do not attempt transcoding |
| WAV header or frame data is malformed or truncated | `422 Unprocessable Content` | Reject as invalid audio |
| Sample width is not 2 bytes | `422 Unprocessable Content` | Report unsupported sample width |
| Channel count is not 1 | `422 Unprocessable Content` | Report that mono audio is required |
| Sample rate is below 8,000 Hz or above 48,000 Hz | `422 Unprocessable Content` | Report the accepted range |
| Duration is below 0.5 seconds or above 30.0 seconds | `422 Unprocessable Content` | Report the accepted range |

HTTP error responses use FastAPI's JSON error shape with a `detail` field.
Error text should identify the failed rule without exposing stack traces or
internal decoder details.

If multiple WAV properties are unsupported, Version 1 may report the first
failure encountered. Validation order must remain deterministic and covered by
tests.

## Response

For accepted audio, the response contains:

- `snore_detected`: a boolean decision.
- `confidence`: a number in the inclusive range `[0.0, 1.0]`.

The exact Version 1 signal-processing decision policy will be documented before
the detector is implemented.

## Security and Resource Boundaries

- Do not trust the client-provided filename or MIME type as content validation.
- Do not persist uploaded audio in Version 1.
- Do not include audio bytes or local paths in logs or error responses.
- Decode and process the upload in memory only after the bounded size check.
- Reject malformed inputs with controlled client errors rather than server
  errors.
