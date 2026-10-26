# ARTERIO — Vascular Screening

A local vascular-screening research application for the Congressional App Challenge, formerly PulseForm. Explore optical pulse waveforms and the anatomy behind the signal.

Built together by Varsh G. and Shreyas. Varsh has led substantial UI work; Shreyas has made substantial contributions to the mathematical and signal-processing work. Both contribute to the shared project.

## Run on macOS

From this folder in VS Code:

```sh
.venv/bin/python -m streamlit run app_and_ml/app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open http://127.0.0.1:8501. Stop with Control-C. The current virtual environment already contains the dependencies. Requirements select the existing desktop OpenCV package on macOS and the headless package on other platforms; only one OpenCV distribution should be installed. For a new environment, install `requirements.txt` before running.

The black-and-cyan ARTERIO opening plays once per browser-tab session. Click the ARTERIO name in the header to replay. The opening finishes automatically after 2.8 seconds; Escape dismisses it from the keyboard. Reduced-motion preferences bypass it. The solid atlas uses white tissue, grey coronary vessels and cyan selection.

## Pages

- Telemetry: recording guide recommends 1080p / 60 FPS, 20–25 seconds and light contact; upload original MP4/MOV/AVI files, with a retake/reset action; decode with OpenCV, hold short clips for explicit consent, cap decoding at 25 seconds, trim 2 seconds at the start and 1 at the end, apply PCHIP/SOS processing, and estimate experimental pulse descriptors.
- Heart Explorer: local WebGL/GLSL point cloud, sourced circulation chapter, rotatable BodyParts3D reference atlas, keyboard controls, and 28 selectable structures, including four source-mapped valve assemblies. The original procedural point cloud is preserved at the top. The scene fills the browser viewport and follows the website scroll. All portal rings have been removed. The included SVGs provide labeled internal-anatomy references with attribution.
- Cohort Analytics: clearly labeled simulated observations.
- Clinical Docs: physiology, acquisition methods, validation status and sources.
- Architecture: an alternating left/right flowchart with rounded cyan connections, a scroll-driven progress dot, expandable engineering details, and a reproducible local DSP benchmark.

The heart uses JavaScript, HTML/CSS, WebGL and GLSL, with a Canvas 2D fallback. The dashboard and processing use Python, Streamlit, Plotly, NumPy, SciPy and OpenCV. No Three.js, Java, SQL, cloud tasks or hosted services were added. The pre-existing Google Fonts import requires internet; heart rendering and video processing use local resources.

## Research status

This app has no established diagnostic accuracy or validated risk thresholds. SI now uses entered height divided by secondary-landmark delay (m/s); RI is foot-referenced and expressed as a percentage. These replace the earlier dimensionless timing and amplitude ratios. Upsampling does not add captured temporal information. Smoothed APG derivatives and b/a candidates are available, but landmark accuracy and vascular-age inference are not validated.

The existing `vascular_model.pkl` is a legacy artifact trained on synthetic variance targets and is never loaded by the live app. `train.py` now requires independent outcome labels and subject IDs; it refuses to manufacture clinical labels from SI. No replacement model has been trained because those labels and verified dataset sampling metadata are unavailable. Original training code is preserved in `docs/reference/train-original.py` for provenance.

See [technical brief](docs/TECHNICAL_BRIEF.md), [application wording](docs/RESUME.md), [source record](docs/PROVENANCE.md), and [verification](docs/VERIFICATION.md).

See [team integration decisions](docs/INTEGRATION.md) for the comparison with Shreyas’s changes.

See [project map](docs/PROJECT_MAP.md) for file responsibilities. Runtime comments were simplified; archived reference snapshots and the large dataset were preserved.

## Checks

```sh
.venv/bin/python -m unittest discover -s tests -v
```

## Development tools

Claude and Codex were used as coding assistants. The team reviews the implementation and tests changes with generated signals, video fixtures and interface checks. Shreyas’s work report also documents earlier real-recording trials; those clips were not supplied for the current review.
