# PulseForm

Measure heart rate and arterial stiffness from a 20-second phone video of your fingertip.

> PulseForm is an educational project, not a medical device. It does not diagnose, treat or screen for any condition.

## How it works

1. Cover the phone's back camera and flash with a fingertip and record about 20 seconds.
2. `video_pipeline.py` averages the red channel of every frame, then resamples the signal to a uniform 100 Hz with a cubic spline (phone frame rates drift).
3. `math_engine.py` applies a zero-phase 0.5-5 Hz Butterworth bandpass filter, detects each heartbeat, and finds the reflected-wave bump in every beat.
4. The app reports:
   - **Heart rate** from the spacing between heartbeats.
   - **Stiffness Index (SI)** = 1 / (reflection delay as a fraction of the beat). A stiffer artery returns the reflection sooner, so SI is higher. Using a fraction of the beat keeps heart rate from distorting it.
   - **Reflection Index (RI)** = reflection height / main peak height.
5. A signal-quality check rejects recordings with a weak or irregular pulse and asks for a re-recording instead of reporting a number.

## Run it

    git clone https://github.com/VarshG75/PulseForm.git
    cd PulseForm
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    streamlit run app_and_ml/app.py

Then open http://localhost:8501, upload an .mp4 or .mov of your fingertip, and press the analysis button. A 1080p video can take up to a minute to process.

## Project layout

- `app_and_ml/app.py` - Streamlit interface
- `app_and_ml/signal_processing/math_engine.py` - filter, beat detection, Stiffness and Reflection indices
- `app_and_ml/signal_processing/video_pipeline.py` - video to signal, resampling, `analyze_live_video()`
- `app_and_ml/views/` - additional app pages (cohort illustration, background, architecture)

## Testing

- Synthetic finger videos with a known answer: a 72 BPM healthy profile returns about 73.6 BPM, and the stiff profile returns a higher Stiffness Index (4.15) than the healthy profile (2.33).
- One real fingertip recording (iPhone, 20 s, 1080p) returned 64.3 BPM, and an independent frequency analysis of the same signal gave 63 BPM.
- Poor recordings (finger not covering the flash, motion) are rejected by the quality check.

## Limitations

- Needs a still hand and full coverage of the camera and flash.
- The Stiffness and Reflection indices have not been validated against clinical measurements.
- The Cohort Analytics page shows a simulated illustration, not real patient data.
- iPhone HEVC .mov files work in our tests, but very old OpenCV builds may not open them; use H.264 .mp4 if needed.

## AI use

We used Claude (Anthropic) as an AI coding assistant. We tested the code against recordings and synthetic videos with known answers, and we found and fixed errors along the way, including replacing placeholder data with the real analysis pipeline.
