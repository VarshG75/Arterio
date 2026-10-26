# Review of Shreyas's work report

Reviewed October 26, 2026 against the shared repository through upstream commit `1ef661c` and the current integrated implementation. The four-page report describes an earlier PulseForm release. Its real-video results are reported by Shreyas; the original clips and test fixtures were not provided for this review. The original PDF was not changed or added to the repository.

## Contribution record

The report and repository history identify Shreyas's substantial work on the math engine, recorded-video ingestion, the app's real analysis call, interval-quality checking and correction of unsupported claims. Varsh's substantial UI work remains in the integrated application. These are complementary contributions to a shared project; comparing only the latest commits would understate Shreyas's work.

## Corrections and qualifications

| Report statement | Review |
| --- | --- |
| Frequency analysis of the same optical signal is an independent heart-rate check. | It is a useful algorithmic cross-check, but not an independent reference measurement. Both methods inherit the same recording artifacts. An external reference is needed to assess measurement accuracy. |
| Generated videos prove the math works. | They test the selected inputs and expected behavior. They do not establish general correctness, device compatibility or clinical accuracy. |
| Normalizing delay by the beat period removes heart-rate distortion. | The earlier value is `Q = Tcycle / delay`, a dimensionless descriptor. At a fixed delay it still changes with cycle duration. It is distinct from the height/delay SI definition in m/s. |
| Minimum peak spacing fixes doubled heart rate. | It helps with close secondary bumps, but does not prevent every double detection. Slow generated profiles can still be ambiguous; the timing guard withholds outputs in those cases. |
| The pipeline trims before filtering. | The upstream implementation at `1ef661c` filters before trimming. The report's sequence should match the revision it documents. The current pipeline intentionally trims the raw capture before interpolation and filtering. |
| The implementation supports 40–180 BPM. | The older quality gate used those bounds, but its peak detector used a 140 BPM separation limit. The current detector and timing gate use matching 40–160 BPM limits. This is a processing bound, not proof of accuracy across that range. |
| Author line and project name. | Page 1 uses the handle `@sam` and the name PulseForm. Confirm the intended author attribution and use ARTERIO for the current project. Preserve historical names if the report is explicitly labeled as an earlier milestone. |

## Historical values that should not be presented as current results

The earlier release uses 100 Hz cubic-spline resampling, a third-order Butterworth prototype at 0.5–5 Hz, a five-second minimum and dimensionless timing/amplitude ratios. The integrated version uses 200 Hz PCHIP, SOS filtering, smoothed derivatives, beat-template checks, explicit short-clip consent, height/delay SI in m/s and foot-referenced RI as a percentage. Its values are not directly interchangeable with the report's SI and RI. Updated results need a clearly identified code revision and new runs; the report's real-video measurements were not reproduced here.

## Which implementation to keep

- Keep Shreyas's real-upload integration, explicit failure behavior, timing consistency check and accurate simulation disclosures. These are important corrections to the earlier application.
- Keep the integrated UI, recording state/reset handling, bounded decoding, timestamp checks, SOS representation and shared quality gates. [SciPy recommends SOS filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html) to reduce numerical problems with transfer-function coefficients.
- Keep the full-frame OpenCV reduction. The audit found that sparse regular-grid sampling could misclassify structured frames as overexposed. The replacement computes the full mean without the old NumPy reduction overhead.
- Keep SI/RI definitions explicit. The [height/delay SI formulation](https://pubmed.ncbi.nlm.nih.gov/12241535/) differs from the older cycle-normalized ratio; use the correct units and avoid unvalidated risk tiers.
- Treat PCHIP, the broader filter band and derivative/shoulder choices as implementation decisions requiring evaluation. More processing stages and a denser interpolation grid do not establish greater medical accuracy. There is no evidence here to declare one version more accurate on real fingers without the original clips and an independent reference.

## Presentation updates

The header and browser title now use Vascular Screening. The interface leads with measured pulse features, acquisition guidance, explicit units and scoped performance numbers. Simulation labels and a concise research-use/validation statement remain visible. The architecture headline reports its measured P95 signal-processing time rather than a broad latency target; video decoding is explicitly excluded.

Shreyas's verified local-context contribution is retained with a direct source: the [2022 Williamson County Community Health Assessment](https://www.healthywilliamsoncounty.org/content/sites/wcchd/2022cha/2022WilliamsonTXCHA_FINAL.pdf), which ranks heart diseases first among county causes of death in 2020. That historical context motivates the project but does not demonstrate screening performance.

AI-assistance disclosure is retained in the README. The [Congressional App Challenge judging guidance](https://www.congressionalappchallenge.us/congress/congressional-toolkit/) emphasizes programming understanding, idea quality, user experience and implementation. Precise, reproducible explanations support those criteria more directly than unsupported clinical or performance claims.
