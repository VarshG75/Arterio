# Team integration — October 26, 2026

Compared local work on `main` with Shreyas’s fetched commits through `33906dd`. A backup of all modified/untracked work and the original HEAD is saved outside the repository at `/tmp/arterio-before-integration-20261026-103509`.

| Upstream change | Integration decision |
| --- | --- |
| `ccb50fb`: dependencies | Use the headless OpenCV distribution because the app does not open native OpenCV windows. Allow NumPy 2.5.1–2.5.x to accommodate the existing local version and upstream’s 2.5.2 pin. Preserve the other matching dependency pins. |
| `cea3c9c`: red-channel pixel sampling | Adopt the stride-4 reduction for normal-size frames; keep full reduction below 64 pixels on either axis. It is an approximate spatial mean, reducing the number of sampled pixels by about 16×. Decoder work is unchanged. |
| `cea3c9c`: interval consistency | Adopt coefficient of variation ≤0.20. Match the supported BPM range to the current detector’s 40–160 limits. Withhold SI/RI and pulse frequency on timing failure, and explain that uneven intervals can have multiple causes. This is an engineering gate, not a diagnosis. |
| `cea3c9c`: start/end trim | Keep the existing shared 2-second start / 1-second end trimming before interpolation. Do not apply the upstream trim a second time. |
| `cea3c9c`: assessment wording | Preserve current measured-only results. Old dimensionless SI thresholds cannot be applied to the newer height/delay SI in m/s. |
| `33906dd`: simulated cohort labels | Keep the richer interactive cohort interface and its existing simulation disclosures. Make the top label explicitly say SIMULATED DATA STUDY. |
| Local UI and numerical engine | Preserve the navigation, opening, heart atlas, scroll flowchart, recording consent, retake, modular views/services, PCHIP, SOS filtering, smoothed derivatives and beat-template quality checks. Upstream does not modify `math_engine.py`. |

The source GLB, reference images, geometry mappings, licenses, large CSV and legacy saved model are retained. The unrelated personal `.vscode/extensions.json` recommendation is excluded from the integration commits.

Validation: 20 regression tests, array self-check, all five Streamlit routes, JavaScript syntax and whitespace checks. Generated signals/videos verify software behavior, not clinical accuracy. Spatial-sampling tests cover uniform signals, small-frame fallback and bounded error on generated pixel noise; they do not establish equivalence for every real recording.
