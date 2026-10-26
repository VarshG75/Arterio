# ARTERIO — evidence-grounded application wording

Use the team role only if it accurately reflects your own contribution. These drafts describe implemented software, not clinical efficacy.

## Common App description (144 characters)

Built ARTERIO: Python video pulse analysis with OpenCV/SciPy, an interactive 3D heart atlas, and a Streamlit dashboard for waveform exploration.

## Technical CV bullets

- Built a recorded-video pulse pipeline using OpenCV red-channel extraction, 200 Hz PCHIP interpolation, and forward/backward SOS Butterworth filtering.
- Implemented optical peak detection and experimental reflection timing/amplitude descriptors with explicit quality failures and no substituted measurements.
- Integrated a WebGL/GLSL BodyParts3D reference atlas with 28 selectable groups, keyboard rotation, a point-cloud view, and sourced blood-flow education.
- Separated Streamlit styling and view modules; added decoder regression checks with generated videos and labeled synthetic cohort examples.
- Established an offline classifier entry point requiring independently labeled features and subject-level holdout; clinical validation remains future work.

## Interview preparation

- Explain why 200 Hz interpolation is different from acquiring 200 frames per second.
- Distinguish filter passband from peak-detector limits, and offline zero-phase processing from live latency.
- Explain why height/delay SI and foot-referenced RI differ from the earlier dimensionless ratios, and why they require validation.
- Explain why threshold-derived labels cannot independently validate a classifier.
- Describe how numerical APG derivatives differ from validated a/b landmark extraction.
