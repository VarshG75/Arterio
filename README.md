# ARTERIO — Vascular Screening

ARTERIO is a research prototype that analyzes smartphone fingertip videos and provides an interactive heart atlas. It displays optical pulse waveforms, recording-quality information and estimated stiffness and reflection indices.

## Features

- **Telemetry:** video upload, stable-section selection, pulse waveforms, annotated measurements and retake controls.
- **Heart Explorer:** interactive 3D anatomy with selectable structures and source credits.
- **Cohort Analytics:** an explicitly simulated dataset for exploring example trends.
- **Clinical Docs:** physiology, recording guidance, methods and scientific references.
- **Architecture:** an interactive processing flowchart and reproducible signal-processing benchmark.

## Requirements

- Python **3.14** and pip. Enable Python on PATH when installing on Windows.
- A recent browser.
- Node.js is optional and only needed for the JavaScript navigation tests.

The application has been tested on macOS with Python 3.14. Windows and Linux setup commands are provided below; those operating systems have not been independently tested.

## Install and run

Download or clone the repository and open a terminal in its root folder.

### Windows — PowerShell

These commands use the virtual environment directly, so PowerShell activation is not required.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app_and_ml/app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

If the Python launcher is unavailable, use `python -m venv .venv` after confirming that `python --version` reports Python 3.14.

### macOS — Terminal

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app_and_ml/app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

### Linux — terminal

Install Python 3.14 with its pip and venv support using the instructions for your distribution. Then run:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app_and_ml/app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open [http://127.0.0.1:8501](http://127.0.0.1:8501). Stop the server with **Ctrl+C**.

Requirements choose desktop OpenCV on macOS and headless OpenCV on Windows/Linux. Both can decode video; do not install both packages in the same environment. If port 8501 is occupied, use `--server.port 8502` and open the corresponding address. Google Fonts requires an internet connection; bundled heart assets and video processing are local to the app server.

## Record a sample

1. Rest the phone and your hand on a table. Use the rear camera with its flash/video light **ON throughout**, rather than Auto or Off.
2. Cover the lens and adjacent light with light fingertip contact. Enable **AE/AF lock**, if available, to keep exposure and focus fixed. Stop if the phone or finger becomes uncomfortable.
3. Record **20–25 seconds**, preferably at **1080p / 60 FPS**. 720p and 30 FPS are also supported.
4. Upload the original MP4, MOV or AVI file. Confirm the recording settings and enter height in centimeters or feet and inches.
5. Review the waveform, selected interval and measurement details. Use **Retake / replace video** for another attempt.

The first 2 seconds and final 1 second are trimmed. Stability checks then select the longest continuous usable section; at least 8 seconds must remain. Separate sections are never joined. Uploads under 12 seconds are rejected; uploads from 12 to under 20 seconds require explicit approval. Decoding is limited to a nominal 25-second segment. Measurements remain unavailable when the required checks fail.

## Methods and limitations

The pipeline uses full-frame mean red intensity, a 200 Hz PCHIP processing grid, Butterworth filtering in second-order sections, smoothed derivatives and pulse-feature detection. Resampling does not add information beyond the camera's captured frame rate.

Stiffness Index uses entered height divided by a secondary-feature delay, in m/s. Reflection Index compares secondary and primary amplitudes relative to the pulse foot, in percent. Their accuracy in this smartphone implementation has not been clinically established. The application does not diagnose disease, measure blood pressure or report validated risk categories.

The saved `vascular_model.pkl` is a legacy artifact and is not loaded by the application. The training utility requires independently labeled features and subject identifiers. The included CSV is separate from the live video pipeline and the simulated Cohort page; see [dataset source](docs/DATASET_SOURCE.md).

## Technical documentation

- [Processing methods](docs/TECHNICAL_BRIEF.md)
- [Recording quality and thresholds](docs/SIGNAL_QUALITY.md)
- [Architecture evidence and benchmark scope](docs/ARCHITECTURE_EVIDENCE.md)
- [Testing and validation scope](docs/VERIFICATION.md)
- [Project structure](docs/PROJECT_MAP.md)
- [Asset credits and licenses](docs/ASSET_CREDITS.md)

## Run the checks

**Windows — PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test tests/test_navigation.cjs
```

**macOS / Linux:**

```sh
.venv/bin/python -m unittest discover -s tests -v
node --test tests/test_navigation.cjs
```

The tests cover numerical behavior, generated video inputs, recording-quality checks, upload state, page routing and asset integrity. They do not establish clinical accuracy. The Architecture benchmark measures selected-array processing separately from upload handling, decoding, stability selection and rendering.

## License and development tools

Application code is available under the [MIT license](LICENSE). Anatomy models, reference diagrams and the dataset have separate source terms. Required third-party credits are retained alongside the assets and in the viewer.

Claude and Codex were used as coding assistants. We review the implementation and test changes with generated signals, video fixtures and interface checks.
