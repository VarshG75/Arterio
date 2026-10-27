# Project map

| Location | Responsibility |
| --- | --- |
| `app_and_ml/app.py` | Dashboard setup and page routing |
| `app_and_ml/views/navigation.py` | Page names and URL synchronization for refreshes |
| `app_and_ml/styles.py` | Shared colors, navigation, uploads and warning styles |
| `app_and_ml/views/capture.py` | Upload state, duration consent, height input and retake |
| `app_and_ml/views/height.py` | Centimeter and feet/inches entry, conversion and input validation |
| `app_and_ml/views/acquisition.py` | Shared recording protocol content |
| `app_and_ml/views/telemetry.py` | Analysis workflow, decoding progress and measured results |
| `app_and_ml/views/waveform.py` | Measured landmark plots and per-beat SI/RI explanation |
| `app_and_ml/assets/telemetry/` | Telemetry-specific responsive layout |
| `app_and_ml/assets/brand/navigation.css` | Shared responsive navigation |
| `app_and_ml/assets/clinical/` | Clinical Docs reading layout |
| `app_and_ml/services/recordings.py` | Temporary-file lifecycle for local uploads |
| `app_and_ml/signal_processing/capture_policy.py` | Shared capture limits and motion heuristic |
| `app_and_ml/signal_processing/video_pipeline.py` | Bounded OpenCV decoding and quality gates |
| `app_and_ml/signal_processing/stability.py` | Raw-signal artifact checks and continuous-window selection before filtering |
| `app_and_ml/signal_processing/math_engine.py` | NumPy/SciPy array API, landmarks and self-check |
| `app_and_ml/views/heart.py` | Local heart asset embedding |
| `app_and_ml/assets/heart/` | Renderer, licensed geometry, mappings and references |
| `app_and_ml/views/architecture.py` | Engineering dossier content |
| `app_and_ml/assets/architecture/` | Flowchart styles, motion and benchmark record |
| `app_and_ml/views/cohort.py` | Clearly labeled simulated data study |
| `app_and_ml/views/clinical_docs.py` | Research explanations and source links |
| `app_and_ml/views/opening.py`, `assets/brand/` | Page entrances and independent scroll memory |
| `app_and_ml/train.py` | Offline training from independently labeled features |
| `scripts/` | Asset preparation, signal benchmark and bounded CSV preview |
| `tests/` | Generated-video, numeric, state and asset regressions |
| `docs/` | Current implementation, source and verification records; `ARCHITECTURE_EVIDENCE.md` maps page claims to evidence and `SITE_REVIEW.md` records prioritized improvements |
| `docs/reference/` | Historical snapshots preserved for provenance |

The runtime source and current documents were reviewed for stale claims and unnecessary comments. Historical reference snapshots, third-party credits, `.git`, the virtual environment, the user's VS Code settings, the legacy model binary and dataset contents are preserved. The large CSV was not scanned. `app_and_ml/explore.py` remains a compatibility entry point for `scripts/inspect_dataset.py`, which reads a bounded row only when explicitly run.
