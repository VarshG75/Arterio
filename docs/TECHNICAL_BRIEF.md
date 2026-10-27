# ARTERIO — optical pulse exploration

ARTERIO is a local Streamlit research prototype for the Congressional App Challenge. It processes recorded fingertip video and provides an educational heart atlas. Software checks on generated signals do not establish clinical accuracy.

## Recording and file handling

The app recommends an original 20–25 second recording at 1080p or 720p, preferably 60 FPS; 30 FPS is supported. Its five acquisition rules cover a supported phone/hand, light contact, fixed exposure/focus where available, comfortably warm hands and practical resolution/frame rate.

OpenCV reads duration metadata before analysis. Under 12 seconds is rejected; 12 to under 20 seconds requires an explicit reduced-window action. A temporary file supplies the decoder and is removed after inspection or analysis, including failures. Decoding has a nominal 25-second frame-count cap. After removing the first 2 seconds and final 1 second, raw-signal stability checks select the longest continuous section of at least 8 seconds. Flagged sections have 1-second margins and are excluded before filtering. Separate sections are never joined. A 20-second recording supplies approximately 17 seconds before stability and beat rejection. Height can be entered in centimeters or feet/inches and is converted to meters for SI. See [signal quality](SIGNAL_QUALITY.md).

OpenCV computes the full spatial red-channel mean, avoiding regular-grid sampling bias. Frame means outside 30–250 and flat sections are excluded. Half-second frame-difference windows are compared with a median variance from 2-second reference windows; excessive variance, large or isolated jumps, high-frequency noise and timestamp gaps flag further sections. The longer reference and a 99th–1st percentile span protect slower narrow pulses from false motion flags. These are recording heuristics, not calibrated SNR, pressure or blanching measurements. Missing FPS uses a disclosed 30 FPS fallback. Available monotonic frame timestamps define the interpolation clock; otherwise nominal FPS is used and a notice explains the fallback.

## Numerical pipeline

PCHIP interpolation creates a uniform 200 Hz computational grid without adding captured temporal detail. It preserves shape on monotone intervals and has C¹ continuity; second derivatives may jump at knots. A fourth-order Butterworth prototype at 0.5–8.5 Hz becomes an eighth-order digital bandpass represented as second-order sections. Forward/backward SOS execution has zero phase shift and requires the recorded segment.

A 0.35-second moving-mean detrended trace is available separately. Primary peaks and feet are located on the bandpassed contour because aggressive detrending can create extra extrema. A 15-sample quadratic Savitzky–Golay fit produces VPG and APG derivatives.

Pulse intervals must fall within the prototype’s 40–160 BPM range and have coefficient of variation at most 0.20; otherwise timing and reflection outputs are withheld. This heuristic does not identify the cause of uneven intervals. Candidate beat segments are normalized to 100 samples and compared with their median template using Pearson correlation. Segments below 0.80 are excluded. Secondary maxima are searched within 10%–55% of the detected cycle; a descending-slope VPG maximum can supply a shoulder candidate. A VPG maximum corresponds to an APG positive-to-negative crossing; the supplied directive's negative-to-positive fallback would identify a VPG minimum and was not used.

Experimental SI is entered height divided by secondary-landmark delay (m/s). RI is secondary amplitude divided by primary amplitude, both relative to the preceding pulse foot, expressed as a percentage. At least four repeatable segments and four secondary candidates are required. Missing values remain unset; values are not forced into expected clinical ranges. This version replaces the previous dimensionless cycle/delay metric and zero-centered amplitude ratio. Historical values are not interchangeable with these outputs. APG b/a candidates are exploratory; no vascular age, diagnosis or disease tier is assigned.

References: [Millasseau et al., 2002](https://pubmed.ncbi.nlm.nih.gov/12241535/), [Takazawa et al., 1998](https://pubmed.ncbi.nlm.nih.gov/9719069/), [SciPy PCHIP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html), [SOS filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html). These references do not validate ARTERIO's thresholds or camera measurements. Twenty seconds and the 25-second cap are application choices, not universal clinical or thermal limits.

## Anatomy and interface

The opening procedural point cloud retains its geometry, shifted 15 CSS pixels right and enlarged about 2%. The lower solid atlas uses BodyParts3D source meshes with white tissue, grey coronary vessels and cyan selection. It has 28 selectable groups, including four valve assemblies and three added coronary venous structures. Internal valves and chamber cavities isolate on selection. All atlas parts share the same display proportion adjustment; this educational illustration is not intended for anatomical measurement. Source files, structure mappings, licenses and checksums are retained.

The architecture page uses alternating cards, rounded scroll-traced cyan connectors and expandable engineering details. Its benchmark is rerun from `scripts/benchmark_dsp.py`; the JSON records measured median, P95, machine and scope. The current benchmark uses 1,000 already-trimmed generated source points at 60 Hz and produces 3,330 processing points at 200 Hz. Across 200 runs after 20 warm-ups on Darwin arm64, it measured 1.413 ms median / 1.520 ms P95 and completed SI/RI reporting. The record includes raw timings, software versions and source hashes. Upload handling, decoding, capture gates, stability selection, trimming and UI rendering are excluded. See [claim audit](ARCHITECTURE_EVIDENCE.md).

## Research work still required

The legacy saved model is never loaded by the app. Training requires independently labeled features and subject IDs, with a subject-level holdout. The supplied CSV's provenance, sample rate and labels have not been verified, and its rows were not audited during this revision. No clinical accuracy, diagnostic equivalence, blood pressure, FDA clearance or reimbursement result is claimed.
