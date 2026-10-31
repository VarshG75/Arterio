# Optical pulse processing

ARTERIO processes original smartphone fingertip videos and displays the resulting optical pulse signal. It is a research prototype; software checks do not establish clinical screening accuracy.

## Acquisition

Record 20–25 seconds with the rear video light on throughout, light fingertip contact and the phone supported. Prefer 1080p / 60 FPS; 720p and 30 FPS are supported. Exposure and focus should remain fixed where the camera supports locking them.

Uploads under 12 seconds are rejected. Uploads from 12 to under 20 seconds require explicit approval. A temporary file supplies the OpenCV decoder and is removed afterward. Decoding has a nominal 25-second frame-count cap.

The initial 2 seconds and final 1 second are trimmed. Raw-signal checks select the longest continuous stable section, requiring at least 8 seconds. Flagged intervals have 1-second margins. Separate sections are never joined. See [recording quality](SIGNAL_QUALITY.md).

## Signal processing

1. Compute the full-frame mean red-channel intensity.
2. Use monotonic decoder timestamps where available, or a disclosed nominal-FPS fallback.
3. Resample with shape-preserving PCHIP interpolation onto a 200 Hz processing grid.
4. Apply a fourth-order Butterworth prototype at 0.5–8.5 Hz as a bandpass in second-order sections, forward and backward.
5. Detect primary peaks and pulse feet on the filtered contour.
6. Estimate derivatives using a 15-point quadratic Savitzky–Golay fit.
7. Compare normalized beat segments with a median template and check interval consistency.
8. Search for secondary peaks or shoulder candidates within 10%–55% of the cardiac cycle.

The processing grid does not add captured temporal information. Forward/backward filtering has zero phase shift but requires the recorded segment; it is not a zero-latency streaming measurement.

A separate 0.35-second moving-mean detrended trace is available for inspection. Landmark detection uses the bandpassed contour.

## Measurements

Stiffness Index is entered height divided by the secondary-feature delay, reported in m/s. Reflection Index compares secondary and primary amplitudes relative to the pulse foot, reported as a percentage. Height entry accepts centimeters or feet and inches.

The pipeline requires at least four accepted beat segments and four secondary candidates for SI/RI reporting. Pulse timing must meet the supported 40–160 BPM processing range and interval-variation limit. Missing results remain unset.

These indices and secondary-feature estimates have not been validated for this smartphone implementation. No diagnosis, blood pressure, vascular age or disease tier is assigned.

References: [Millasseau et al., 2002](https://pubmed.ncbi.nlm.nih.gov/12241535/), [Takazawa et al., 1998](https://pubmed.ncbi.nlm.nih.gov/9719069/), [SciPy PCHIP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html), [SOS filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html).

## Interface and assets

The Streamlit dashboard displays recording quality, annotated waveforms and measurement details. Heart Explorer uses a procedural opening illustration and a sourced BodyParts3D atlas. The atlas is educational and is not intended for anatomical measurement.

The Cohort page uses explicitly simulated observations. It does not represent the uploaded recording or a clinical cohort. The legacy saved model is not loaded by the application.

See [Architecture evidence](ARCHITECTURE_EVIDENCE.md), [validation scope](VERIFICATION.md) and [asset credits](ASSET_CREDITS.md).
