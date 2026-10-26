# Verification — October 26, 2026

## Automated checks

- 27 Python regression tests pass using generated signals, videos and route checks. Checks include duration boundaries, explicit short-clip consent, result badges, saturation/flat-signal rejection, 25-second clamping, 2/1-second trimming, PCHIP shape preservation, SOS stopband behavior, derivative accuracy, bounded feet, peak/shoulder detection, missing values, motion warnings and retake reset. Page URLs select the intended view after refresh, navigation updates the URL, and unknown routes fall back to Telemetry.
- Five Node tests cover independent scroll memory, widget reruns, duplicate navigation events, rapid page changes, refresh initialization and temporary scroll-height clamping during view replacement.
- All five Streamlit routes render without exceptions with AppTest. The Telemetry workflow tests run through upload inspection, confirmation, analysis and result rendering for 15- and 20-second fixtures.
- Heart asset checks verify the unchanged base GLB hash, 17 source-mapped extras, finite positions/normals, valid indices and preservation of the opening geometry, allowing comment-only edits.
- Embedded heart, opening and architecture JavaScript passes `node --check`. Python source parses and `git diff --check` passes.
- The array self-check recovers the ordering of two known generated profiles: SI approximately 7.95 and 15.91 m/s, RI approximately 63.9% and 37.4%. The earlier secondary feature uses the shoulder branch. A warmed 20-second-array run meets the local 25 ms check. These are software checks, not clinical results.
- The architecture benchmark records 0.970 ms median / 1.087 ms P95 across 200 warmed 1,000-sample runs on Darwin arm64 / Python 3.14.3. Scope includes PCHIP, SOS design/execution, detrending, segmentation, template comparison, ratios and smoothed derivatives. Video decoding and rendering are excluded.

## Browser checks

- Chrome verified the 20-seconds+ capture guide and Telemetry heading without the 01 prefix.
- Chrome verified the first heart's preserved point-cloud design with a 15 CSS-pixel right shift and slight enlargement.
- Chrome verified the solid atlas with white surfaces, grey coronary vessels, a narrower/longer display silhouette and cyan surface highlighting. The atlas contains 28 selectable groups, including the added coronary sinus, great cardiac vein and middle cardiac vein. All atlas pieces share the same runtime display proportion transform; normals and picking use the transformed data.
- Existing chapter transitions, the cited grayscale cross-section, the shared cyan navigation and alternating architecture flowchart are retained. Page entrances complete automatically and have no Skip Intro control.
- Chrome verified scrolled Clinical Docs → Architecture starts at the Architecture heading, and returning to Clinical Docs restores its own position. The black-and-white Heart Explorer entrance uses a heart logo below the visible navigation. Refreshing a scrolled Heart Explorer retains its route and replays that entrance. Chrome verified ARTERIO entrances after refreshing each of Telemetry, Cohort Analytics, Clinical Docs and Architecture. The opening Heart Explorer copy sits higher and uses larger heading/body type.

## Scope and limits

- No real smartphone recording or clinical reference measurement was supplied. Generated fixtures do not establish device compatibility or physiological accuracy.
- Principal structures are source-mapped, but the atlas is simplified: vessel networks, tissue layers and microscopic anatomy are incomplete. Its adapted display proportions are illustrative; no clinical anatomy review or dimensionally faithful measurement model is claimed.
- Every rotated structure, narrow mobile layout, touch interaction, Canvas fallback and OS reduced-motion setting has not been exhaustively exercised.
- Duration, brightness, motion-variance and correlation thresholds are engineering choices. Twenty seconds is the recommended app protocol, not a universal clinical standard. Confidence intervals are not estimated. Missing landmarks stay blank.
- The large CSV and model binary were not scanned or retrained. The legacy saved model is not loaded. Runtime source comments and current documents were reviewed; historical snapshots and third-party credits remain preserved.
- Integration and audit changes are committed locally. No pushes, deployments or cloud tasks were performed. The preview runs locally at `127.0.0.1:8501`.

Team integration and audit checks cover structured-pixel averaging, uniform inputs and small frames, bounded interpolation, malformed decoder timestamps, interval consistency, the compatibility API, upload removal and height-change invalidation. Irregular generated traces do not report SI/RI. See `INTEGRATION.md` for upstream commit decisions.

The follow-up audit found and corrected sparse-grid bias and result-invalidation issues. Active macOS requirement versions match the installed environment, and `pip check` reports no broken dependencies. UI assets and source geometry were not changed by the audit; Telemetry was inspected in Chrome and all page routes are checked with AppTest. See `INTEGRATION.md` for scope and remaining peak-detection limits.

Report/presentation revision: reviewed the four-page Shreyas work report and newer upstream documentation changes through `1ef661c`. The header and page title use Vascular Screening; SI/RI labels, units, benchmark scope and validation status remain explicit. Branding assertion, all five routes and all 24 regressions pass. See `REPORT_REVIEW.md` for report corrections and limits of the version comparison.

Navigation revision: page positions live in the current browser document; a reload starts the selected page at the top and replays its entrance. Widget updates do not replay it. The controller is installed in the host document so its cleanup timers survive Streamlit replacing the bootstrap iframe. The remaining legacy name in the README was removed; historical source snapshots and the report's original-name references remain preserved. No signal-processing logic changed.
