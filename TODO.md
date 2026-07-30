# Project TODOs

## Completed

- [x] Establish the layered FastAPI package structure.
- [x] Implement the health endpoint.
- [x] Create REST foundations for posture, snore, sleep score, sleep report, and
  chat.
- [x] Add request validation, response models, OpenAPI contracts, and endpoint
  tests.
- [x] Implement and integrate the stateless deterministic posture pipeline.
- [x] Identify Ollama as the local AI component.
- [x] Identify Gemini as the remote AI service.

## Next — Version 1 Snore Detection

- [x] Define the Version 1 WAV signal-processing policy and supported WAV
  properties.
- [x] Implement WAV contract validation with deterministic client errors.
- [x] Add boundary tests for encoding, sample width, channels, sample rate,
  duration, truncation, and upload size.
- [x] Implement pure audio decoding and feature extraction.
- [x] Implement the non-ML snore decision logic.
- [x] Replace the snore service placeholder.
- [x] Add algorithm, service, endpoint, and invalid-audio tests.
- [x] Document limitations and avoid describing the detector as AI or ML.

## Ollama Local AI

- [x] Select and document the Ollama model.
- [x] Add environment-based Ollama configuration.
- [x] Create an Ollama integration adapter under `app/integrations/`.
- [x] Add timeout and unavailable-model handling.
- [x] Replace the chat placeholder through the service layer.
- [x] Add mocked integration and endpoint tests.
- [ ] Document local installation and model-pull instructions.

## Gemini Remote AI

- [ ] Select and document the Gemini model.
- [ ] Add environment-based Gemini configuration.
- [ ] Create the Gemini integration adapter.
- [ ] Define a constrained prompt and validated report response.
- [ ] Add timeout, authentication, quota, and upstream-error handling.
- [ ] Replace the sleep-report placeholder through the service layer.
- [ ] Add mocked integration and endpoint tests.

## Remaining Platform Work

- [ ] Implement the sleep-score algorithm.
- [ ] Add configuration validation and structured logging.
- [ ] Review all API error responses and security-sensitive logging.
- [ ] Pin or otherwise lock dependency versions for reproducibility.
- [ ] Add deployment and environment setup documentation.
- [ ] Complete the professional README.
- [ ] Verify the public repository contains no secrets, generated data, or
  private research artifacts.
- [ ] Prepare the final course demonstration.

## Deferred Research Enhancements

- [ ] Add a stateful or streaming posture endpoint.
- [ ] Reintroduce hysteresis, movement detection, and temporal smoothing.
- [ ] Evaluate posture thresholds on labeled datasets.
- [ ] Investigate ML-based snore classification when labeled data is available.
