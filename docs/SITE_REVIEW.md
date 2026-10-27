# Website review — October 26, 2026

**Overall: 8/10 for the current website presentation.** This is an editorial assessment, not a prediction of judging results or an assessment of clinical accuracy.

Reviewed the five page routes in desktop Chrome at the user's existing 110% zoom, the implemented upload/results flow, automated checks and the Architecture source. Follow-up checks exercised Telemetry upload/results at 375 px and shared navigation at 375 and 768 px in Chrome device emulation. Real phone browsers and touch capture remain to be tested.

| Area | Grade | Reason |
| --- | --- | --- |
| Visual identity | 8.5/10 | Consistent cyan/black/white palette, strong serif headings, coherent navigation and integrated heart experience. |
| Navigation and motion | 8/10 | Independent page scroll positions and selective entrances work. The alternating architecture path is distinctive. |
| First-use experience | 7/10 | A visitor must create and upload a suitable video before seeing the main result. A clear example would demonstrate the product faster. |
| Technical explanation | 8/10 | Architecture now maps to the code and a reproducible benchmark. Clinical Docs now uses summary cards, readable line lengths and expandable details. |

## Highest-value improvements

1. **Provide a labeled example recording.** Let a visitor run the real ingestion path with a known demonstration clip. Clearly separate it from their own recording; do not present generated numbers as a personal measurement.
2. **Completed: make the measurements visually traceable.** The result plot marks primary peaks but not the accepted secondary landmarks or feet. Show a selected beat with its foot, primary peak, secondary candidate and measured delay, then connect those to the SI/RI cards. This would make the engineering easier to understand and defend.
3. **Completed: make Clinical Docs easier to scan.** Use a short summary and a circulation/signal diagram, constrain paragraph width to roughly 65–75 characters, and put detailed methods into expandable sections. Current full-width text is harder to read than Heart Explorer's narrower information groups.
4. **Raise the small-text reading scale.** Navigation metadata, captions and some technical labels are small and muted. Increase key labels and check contrast in each state. [WCAG's normal-text contrast criterion](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) provides a useful measurable target; this review is not a complete accessibility audit.
5. **Completed: show the processing stages while decoding.** The existing spinner gives little information during longer video decoding. Actual decode progress and clear stage changes would make the app feel more responsive; signal-only millisecond timings do not describe this waiting time.
6. **Add a concise reference-test record.** Record supported phones/codecs, repeat captures, failures and comparisons with an independent reference where available. This supports the implementation story more than additional unmeasured performance or clinical claims. Also check iPhone Safari, touch controls and narrow layouts before a public demonstration.

## Changes completed during this review

- Removed the requested Implementation Notes footer, external links and its variable-definition sentence from Architecture.
- Corrected the displayed Butterworth call, nominal decoding-cap description, derivative-window wording and candidate acceptance explanation.
- Audited each numeric/algorithmic claim against code, tests, arithmetic or primary documentation: [Architecture evidence](ARCHITECTURE_EVIDENCE.md).
- Replaced the short benchmark fixture, which did not reach the SI/RI reporting threshold, with a complete reporting-path fixture. The refreshed measured P95 is 1.52 ms, with input, environment, exclusions, raw timings and source hashes recorded. Stability selection is outside this signal-only benchmark.
- Follow-up: added real frame-decode progress and elapsed time, an annotated waveform and selectable beat inspector with sample-derived SI/RI formulas, and a Clinical Docs reading layout. Items 2, 3 and 5 above describe the original findings now addressed.
- Made flash ON a prominent required capture instruction and explained AE/AF lock ON. Telemetry controls/plots adapt to phones; the shared navigation adapts across all pages. The signal-processing algorithms remain unchanged.
