# Recording stability checks

The full video and array entry points select a continuous section before interpolation or filtering. Shreyas's interval-consistency gate and the existing beat-template and secondary-landmark checks still run afterward. The filter, SI/RI formulas and derivative calculation are unchanged.

## Order of processing

1. Keep the duration consent rules and nominal 25-second decoding cap.
2. Remove the first 2 seconds and last 1 second. The initial trim is a minimum; it does not assume the finger has settled by then.
3. Flag unsuitable raw brightness samples and windows using the rules below.
4. Extend each flagged interval by 1 second on each side, within the retained recording.
5. Select the longest uninterrupted unflagged section. Require at least 8 seconds in that section. This is an engineering minimum, not a clinical standard or a guaranteed number of beats.
6. Interpolate and filter only that section. Keep its original recording-time offset. Never join sections across discarded footage.
7. Apply the existing beat-template correlation, interval consistency and secondary-landmark reporting checks. A stable raw section can still fail them; missing results remain blank.

The results include the selected interval, its duration, flagged intervals, reasons and the full decoded brightness trace. The timeline makes selection visible. Other clean sections can be left unused because only one continuous section is analyzed.

## Current thresholds

| Check | Rule |
| --- | --- |
| Brightness | Flag each frame mean below 30 or above 250 on the 0–255 red scale. |
| Large jump | Absolute centered frame difference exceeds max(2 brightness units, 8 × robust difference spread, 0.8 × robust signal span). |
| Isolated jump | Difference exceeds max(2 units, 4 × spread, 0.25 × span) and twice both neighboring differences (neighbor floor 1 unit). Endpoints are excluded from this isolated-jump test. |
| Difference variance | Overlapping 0.5-second windows, 50% overlap; variance exceeds 4 × median variance from 2-second reference windows (advanced by 0.5 seconds), with a 0.04 units² floor on the median. The longer reference avoids treating quiet portions of slower pulses as the whole-signal baseline. |
| Flat section | In a 2-second window, 95th–5th percentile brightness span is below 0.2 units. |
| High-frequency noise | In a mean-centered, Hann-windowed 2-second section, FFT power above 8.5 Hz exceeds power from 0.5–8.5 Hz. Windows advance by about 0.5 seconds. |
| Timestamp gap | Adjacent source timestamps differ by more than max(0.15 seconds, 2.5 / nominal FPS). Invalid decoder clocks still use the existing nominal-clock fallback before this check. |

Robust spread is 1.4826 × median absolute deviation of frame differences. The jump check uses the 99th–1st percentile signal span so narrow, slower pulses are not mistaken for isolated jumps. The flat-section test uses the 95th–5th percentile span within its own window. Thresholds are explicit implementation choices, evaluated with generated traces. They are not calibrated SNR, contact-pressure measurements, or a guarantee of physiological accuracy. Motion and exposure changes inside the pulse band may remain undetected. Very weak or unusually shaped genuine pulses may also be rejected.

## Evidence and remaining work

Generated checks cover clean 30/60 FPS signals, late settling, isolated spikes, baseline steps, clipping, repeated disturbances, sustained high-frequency noise, source timestamp gaps, selected-window timestamps and refusal to join short sections. Generated video tests exercise decoding and the same selection path. Existing regressions cover missing landmarks and irregular timing.

Three locally supplied original MOV recordings were also compared with the previous fixed-trim processing path. One formerly passed the software checks; two pass after stability selection, and the other still fails interval consistency. No clinical reference was available. This small acceptance check is not an estimate of sensitivity, accuracy or general compatibility. No real waveform arrays or original recordings are bundled with the tests.

[Papini et al., 2017](https://pubmed.ncbi.nlm.nih.gov/29059824/) describes template-based rejection of corrupted pulse beats. It supports the rationale for quality assessment; its algorithm and performance are not claimed for ARTERIO. Independent annotated phone recordings are still needed to measure rejection mistakes, retained landmark accuracy and performance across cameras and lighting conditions.

The published Architecture benchmark times the already-selected array processing path. It excludes stability selection, video decoding, capture checks and the interface. The on-screen elapsed timer covers the full upload-analysis run.
