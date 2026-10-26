# Team integration — October 26, 2026

Compared local work on `main` with Shreyas’s fetched commits through `33906dd`. This comparison covers the recent commits, not the full extent of Shreyas’s substantial math and signal-processing contributions; the project is co-developed with Varsh. A backup of all modified/untracked work and the original HEAD is saved outside the repository at `/tmp/arterio-before-integration-20261026-103509`.

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

## Follow-up regression audit

- Regular stride-4 sampling could falsely report an overexposed frame: a generated striped image averaged 184.6875 over all red pixels but 255 over the sampled grid. Replaced it with OpenCV full-frame summation divided by the pixel count. This retains the exact spatial mean while reducing Python/NumPy reduction overhead.
- On a local generated 1080p frame, the NumPy full reduction took about 0.70 ms and the OpenCV reduction about 0.24 ms per frame. This narrow measurement excludes decoding and is not a general video speed guarantee.
- Height changes and explicit upload removal now invalidate previous results. Navigating between pages does not invoke the removal callback.
- The compatibility `compute_indices` API now enforces the same interval-quality check as the full pipeline. Timing failure has its own message.
- Broken/nonmonotonic timestamps or implausible gaps fall back to the nominal frame clock. Excessively large interpolation grids are rejected before allocation.
- Dependencies now select the already-verified desktop OpenCV distribution on macOS and the headless distribution elsewhere. The installed packages satisfy all active macOS requirements.

Remaining limitation: the simple peak detector can mistake a pronounced secondary bump for another primary peak, especially in slow generated pulse profiles. The timing guard rejects these ambiguous traces instead of displaying misleading metrics. Real-phone recordings and reference comparisons are still needed to evaluate acceptance and accuracy.

## Work-report review and newer documentation commits

Reviewed Shreyas's four-page work report and fetched newer upstream commits `8340b2e` and `1ef661c`. These update Architecture, Clinical Docs and README rather than the math engine. The current interface retains its scroll flowchart and current processing specifications; source-backed local context and AI-assistance disclosure are incorporated. Both upstream commits remain in the integration history. Detailed historical/current differences and report corrections are in `REPORT_REVIEW.md`.

The presentation now uses Vascular Screening as the product label, explicit SI/RI units, measured P95 signal-processing latency, concise recording instructions and a visible research-use statement. Simulation disclosures, source credits and validation scope remain intact. All 24 regression tests and five page routes pass after the wording changes.
