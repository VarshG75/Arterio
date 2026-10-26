# Architecture claim audit — October 26, 2026

The Architecture page describes implemented software and local measurements. The evidence below does not establish clinical screening accuracy. The page's illustrative waveforms are drawn SVGs, not recordings.

## Claim-to-implementation record

| Page claim | Implementation and check | Interpretation |
| --- | --- | --- |
| Record 20–25 seconds; reject under 12; require approval from 12 to under 20 | `capture_policy.py`: duration constants and `duration_gate`; `video_pipeline.py`: `analyze_live_video`; duration-boundary, short-upload and workflow tests | These are app protocol choices, not clinically validated duration thresholds. |
| Decode no more than `floor(25 × FPS)` frames | `video_pipeline.py`: `extract_red_signal` loop; trimming/clamping tests | A nominal-FPS frame-count cap, not a 25-second wall-clock processing guarantee. Variable timing and decoding speed can differ. |
| Trim first 2 seconds and final 1 second of the processed segment | `math_engine.py`: `clamp_and_validate_buffer`, using ceiling-rounded frame counts; video API slices timestamps to match | Frame-clock trims occur before interpolation/filtering. Longer clips use the beginning of the recording. |
| Use a local temporary file | `services/recordings.py`: `recording_path` writes upload bytes and unlinks the file in `finally` | The browser upload and decoder buffers still consume memory. |
| Full-frame mean red intensity | `video_pipeline.py`: `mean_red_channel` uses `cv2.sumElems(frame)[2] / (height × width)`; structured-pixel and uniform-frame tests | No sparse regular-grid pixel sampling. Complexity of this reduction is O(F × H × W), excluding codec-dependent decoding work. |
| About 6.22 MB per decoded 1080p BGR frame | `1920 × 1080 × 3 = 6,220,800` bytes for an 8-bit three-channel frame | Decimal MB for the raw pixel payload only, not process peak memory. |
| Accept mean red 30–250; warn above 4× variance ratio | `clamp_and_validate_buffer`; `capture_policy.py`: `motion_quality`; brightness/flat-signal and local-spike tests | Motion uses overlapping half-second windows of frame differences, median variance and a `1e-6` floor. This is neither pressure sensing nor a calibrated SNR test. |
| 30/60 FPS recording guidance and frame-clock fallback | Metadata handling and nominal-frame fallback in `video_metadata` / `extract_red_signal`; malformed timestamp test; generated 30 FPS video tests and 60 Hz array tests | No claim that every phone, codec or variable-frame-rate recording was verified. Missing FPS uses 30 FPS and displays a warning. |
| PCHIP resampling at 200 Hz; 5 ms grid; C¹ continuity | `math_engine.py`: `resample_signal`; interpolation/input-validation tests; [SciPy PCHIP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html) | Interpolation adds grid locations, not captured temporal detail. Second derivatives may jump at knots. |
| Finite increasing timestamps; reject excessive interpolation grids | `resample_signal` validates order, matching lengths and maximum grid size of 200,000 points; duplicate-time and unbounded-grid tests | Local PCHIP slope construction takes O(N) work. This bound describes construction, not the complete analysis. |
| Fourth-order prototype, eighth-order one-pass bandpass at 0.5–8.5 Hz | `math_engine.py`: `bandpass_filter`; [SciPy Butterworth design](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html); finite-output/stopband tests | The displayed call now includes `btype='bandpass'` and `output='sos'`. The listed cutoffs are the one-pass −3 dB frequencies. |
| Forward/backward SOS filtering, odd padding at most 600 points per side | `bandpass_filter` uses `sosfiltfilt`, centered input and `min(600, M−1)` padding at 200 Hz; [SciPy SOS filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html) | Zero phase is not zero execution time. Magnitudes multiply across passes; edge artifacts remain possible. Filtering is O(M) at fixed order. |
| Separate 0.35-second moving-mean detrending | `math_engine.py`: `detrend_signal`; `process_trimmed_signal` detects peaks on the bandpassed contour instead | Detrending is available for inspection; it is not the contour used to select landmarks. |
| VPG/APG from a 15-point quadratic Savitzky–Golay fit | `compute_smoothed_derivatives` uses derivative orders 1/2 and `delta=1/200`; quadratic derivative test; [SciPy Savitzky–Golay](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html) | The sample spacing is 5 ms; smoothing changes local morphology. A tiny-array fallback exists outside the normal retained-video length. |
| 40–160 BPM, interval CV at most 0.20 | `detect_cardiac_cycles` and `assess_beat_intervals`; supported-range and irregular-wave tests | Engineering acceptance limits, not validated sensitivity/specificity across that range. |
| Normalize beats to 100 points; template correlation at least 0.80 | `_quality_beats` interpolates foot-to-foot segments and compares them with their median template | Correlation measures shape repeatability. It is not diagnostic confidence. |
| Search 10%–55% of a cycle, before the next foot; delay at least 50 ms | `extract_hemodynamic_indices`: integer sample window, secondary-peak then descending-VPG shoulder candidate, and delay rejection; known-delay tests | The bounds reduce the candidate search. They do not prove a landmark is a reflected wave or eliminate every artifact. |
| SI = entered height / delay, in m/s; foot-referenced RI in percent | `extract_hemodynamic_indices`; known-delay/height-scaling tests; [original digital-pulse SI study](https://pubmed.ncbi.nlm.nih.gov/12241535/) | The source study used an infrared instrument. It does not validate this smartphone pipeline or shoulder detector. |
| At least four repeatable segments and four secondary candidates | `extract_hemodynamic_indices`: `enough` condition; missing-landmark tests | Candidates also require `0 < RI < 100`; unsupported outputs stay missing. No disease tiers, vascular age or blood pressure are computed. |
| O(M²) worst-case peak-prominence search | `find_peaks(..., prominence=...)` without `wlen`; [SciPy prominence strategy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_prominences.html) | Analytical upper bound: O(M) candidates can each scan O(M) points. This is not a measured runtime prediction. |
| Measured P95 latency | `scripts/benchmark_dsp.py`, `assets/architecture/benchmark.json`, and `tests/test_architecture_evidence.py` | See scope below. The timing is not a clinical or device-performance guarantee. |

Implementation files are in `app_and_ml/signal_processing/` unless another path is stated. The tests listed above use generated inputs.

## Corrected benchmark

The earlier fixture contained 1,000 points at 200 Hz: about five seconds. It reached the numerical functions but retained only two repeatable segments, so it did not report SI/RI. It was not sufficient evidence of the completed reporting path.

The current fixture contains **1,000 already-trimmed generated input points at 60 Hz**, resampled to **3,330 points at 200 Hz**. It completes with status `OK`, 15 accepted segments and 15 secondary candidates. These are generated fixture results, not patient outcomes or counts from the CSV dataset.

On this Mac, after 20 warm-up executions, 200 timed executions measured **1.446 ms median / 1.698 ms P95**. The published card rounds P95 to **1.70 ms**. The JSON records every duration, the UTC timestamp, Python/NumPy/SciPy versions, OS/machine details, fixture parameters, result status and SHA-256 hashes of processing code and the benchmark script.

Reproduce locally:

```sh
.venv/bin/python scripts/benchmark_dsp.py
.venv/bin/python -m unittest discover -s tests -q
```

The benchmark includes PCHIP, filter design/execution, detrending, cycle/foot detection, derivatives, template comparison, ratios and interval checks. It excludes upload handling, video decoding, capture gates, trimming and rendering. Timing changes with machine load and software; regenerating it replaces the checked-in measurement. Source-hash checks fail if the measured code changes without a refreshed benchmark.

## Removed from the page

The Implementation Notes footer, its two external links and the variable-definition sentence were removed as requested. Primary source links remain in this evidence record and Clinical Docs. Relevant symbols are defined within the stage details where needed.

## Evidence still needed

Independent real recordings are needed to evaluate device compatibility, reference heart-rate agreement, landmark accuracy and repeatability. The large CSV is unchanged. After the team supplied its Kaggle link, a bounded header/one-row inspection confirmed 2,000 waveform columns plus a Label column; the source describes Normal/MI classes. No age or timing field was found. Source metadata and the remaining verification gaps are recorded in [dataset source record](DATASET_SOURCE.md); the whole CSV was not scanned. The existing 800-row Cohort page remains explicitly simulated.
