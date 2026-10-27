# ARTERIO — Vascular Screening

A local vascular-screening research application for the Congressional App Challenge. Explore optical pulse waveforms and the anatomy behind the signal.

Built together by Varsh G. and Shreyas. Varsh has led substantial UI work; Shreyas has made substantial contributions to the mathematical and signal-processing work. Both contribute to the shared project.

## Run on macOS

Verified with Python 3.14 on macOS. For a fresh checkout, run these setup commands from the project folder:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Start the app from this folder in VS Code:

```sh
.venv/bin/python -m streamlit run app_and_ml/app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open http://127.0.0.1:8501. Stop with Control-C. An existing configured virtual environment can skip setup. Requirements select desktop OpenCV on macOS and headless OpenCV elsewhere; install only one OpenCV distribution.

## Record and analyze a sample

1. Rest the phone and your hand on a table. Use the rear camera with its video light **ON throughout**, rather than Auto or Off.
2. Cover the lens and adjacent light with light, steady fingertip contact. Enable **AE/AF lock** if available to keep exposure and focus fixed. Stop if the phone or finger becomes uncomfortable.
3. Record **20–25 seconds**, preferably at **1080p / 60 FPS**. 720p and 30 FPS are also supported. Upload the original MP4, MOV or AVI file.
4. Confirm the recording checkbox and enter height in centimeters or feet and inches. Clicking Analyze without confirmation shows an orange-red reminder and does not process the video.
5. Review the selected recording interval, waveform and beat inspector. Retake / replace video clears the upload and results for a fresh attempt.

The first 2 seconds and final 1 second are removed. Stability checks can exclude further sections, including a longer settling period. Only the longest continuous section of at least 8 seconds reaches the filter; separate sections are never joined. Short uploads between 12 and 20 seconds require explicit approval, and those below 12 seconds are rejected. Missing measurements remain blank when the recording or beat checks fail.

The shared navigation wraps into centered rows on phones and tablets while retaining the pill design. Each page keeps its own scroll position while the site is open. Navigation updates the page URL, so refreshing keeps the selected page and replays its entrance from the top. Heart Explorer uses a black-and-white heart-logo reveal below the navigation. ARTERIO's black-and-cyan opening covers the full screen, including navigation. Clicking Telemetry plays that opening; clicking Cohort Analytics, Clinical Docs or Architecture opens the page directly. Refreshing any of those four pages still plays the ARTERIO opening. Click the ARTERIO name in the header to replay the current entrance. Each finishes automatically after 2.8 seconds; Escape dismisses it, and reduced-motion preferences bypass it. Changing an input on the current page does not replay the entrance. The solid atlas uses white tissue, grey coronary vessels and cyan selection.

## Pages

- Telemetry: record 1080p / 60 FPS for 20–25 seconds with the rear video light ON and light contact. Upload the original MP4/MOV/AVI and enter height in centimeters or feet and inches. Short clips require approval. Processing is capped at 25 seconds, removes the first 2 and last 1 seconds, then selects the longest section that passes stability checks before filtering. At least 8 continuous seconds must remain; separate sections are never joined. The timeline shows the selected section. Actual decoding progress and an annotated beat inspector explain the results. Telemetry controls and plots adapt to phone widths.
- Heart Explorer: local WebGL/GLSL point cloud, sourced circulation chapter, rotatable BodyParts3D reference atlas, keyboard controls, and 28 selectable structures, including four source-mapped valve assemblies. The original procedural point cloud is preserved at the top. The scene fills the browser viewport and follows the website scroll. All portal rings have been removed. The included SVGs provide labeled internal-anatomy references with attribution.
- Cohort Analytics: clearly labeled simulated observations.
- Clinical Docs: physiology, acquisition methods, validation status and sources.
- Architecture: an alternating left/right flowchart with rounded cyan connections, a scroll-driven progress dot, expandable engineering details, and a reproducible local DSP benchmark.

The heart uses JavaScript, HTML/CSS, WebGL and GLSL, with a Canvas 2D fallback. The dashboard and processing use Python, Streamlit, Plotly, NumPy, SciPy and OpenCV. The existing Google Fonts import requires internet; heart rendering and video processing use local resources.

## Research status

This app has no established diagnostic accuracy or validated risk thresholds. SI now uses entered height divided by secondary-landmark delay (m/s); RI is foot-referenced and expressed as a percentage. These replace the earlier dimensionless timing and amplitude ratios. Upsampling does not add captured temporal information. Smoothed APG derivatives and b/a candidates are available, but landmark accuracy and vascular-age inference are not validated.

The existing `vascular_model.pkl` is a legacy artifact trained on synthetic variance targets and is never loaded by the live app. `train.py` now requires independent outcome labels and subject IDs; it refuses to manufacture clinical labels from SI. No replacement vascular-risk model has been trained because independent vascular-risk labels and verified dataset timing metadata are unavailable. The existing CSV has Normal/MI classification labels, which describe a different task; see [dataset source record](docs/DATASET_SOURCE.md). Original training code is preserved in `docs/reference/train-original.py` for provenance.

See [Architecture evidence](docs/ARCHITECTURE_EVIDENCE.md), [recording stability checks](docs/SIGNAL_QUALITY.md), [image/model license review](docs/ASSET_LICENSE_REVIEW.md), [website review](docs/SITE_REVIEW.md), [technical brief](docs/TECHNICAL_BRIEF.md), [application wording](docs/RESUME.md), [source record](docs/PROVENANCE.md), and [verification](docs/VERIFICATION.md).

See [team integration decisions](docs/INTEGRATION.md) for the comparison with Shreyas’s changes.

See [project map](docs/PROJECT_MAP.md) for file responsibilities. Runtime comments were simplified; archived reference snapshots and the large dataset were preserved.

## Checks

```sh
.venv/bin/python -m unittest discover -s tests -v
node --test tests/test_navigation.cjs
```

The final audit passes 47 Python tests and 6 navigation tests. Tests cover all five page routes, video decoding, quality gates, stable-window selection, height conversion, checkbox confirmation, input invalidation, plotted landmarks and asset integrity. Clean generated pulses across 40–160 BPM at 30/60 FPS check that slower pulses are not incorrectly discarded as motion.

Three supplied MOVs were also checked locally: two pass the current software checks and one remains withheld for inconsistent beat timing. This is a small compatibility check, not clinical validation. The original videos and waveform arrays are not included in the repository. See [verification](docs/VERIFICATION.md) for scope and remaining limits.

Architecture describes the implemented pipeline. Its measured DSP benchmark is separate from video decoding, capture checks and stability selection; the full processing wait is shown by Telemetry's progress timer. Benchmark inputs, raw timings and source hashes are in `app_and_ml/assets/architecture/benchmark.json`.

## Image and model credits

Application code uses the [MIT license](LICENSE). The BodyParts3D atlas and reference diagrams have separate licenses and credits, retained in the viewer and alongside their files. The grayscale diagram adaptations are identified explicitly. See the [asset license review](docs/ASSET_LICENSE_REVIEW.md). Supplied reference photographs are not bundled.

## Development tools

Claude and Codex were used as coding assistants. The team reviews the implementation and tests changes with generated signals, video fixtures and interface checks. Shreyas’s work report documents earlier real-recording trials. Three additional original MOV recordings were checked locally during the stability revision; they are not bundled in this repository, and no independent clinical reference was available.
