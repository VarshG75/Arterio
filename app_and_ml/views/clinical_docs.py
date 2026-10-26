"""Physiology, methods, sources and validation status."""
import streamlit as st
from views.acquisition import render_protocol


def render_clinical_docs_view():
    st.markdown('<div class="section-pill">03 / SCIENCE & METHODS</div><div class="hero-title">Behind the pulse.</div>', unsafe_allow_html=True)
    st.write('ARTERIO brings fingertip optical capture, waveform analysis and heart anatomy into one interface. Explore how the signal is acquired, which features are measured and how the system is evaluated.')
    st.subheader('Why this problem matters')
    st.write('Accessible vascular screening is the project’s long-term goal. The current application measures optical pulse features and helps explain the physiology behind them.')
    st.markdown('Shreyas identified a relevant local source: the [2022 Williamson County Community Health Assessment](https://www.healthywilliamsoncounty.org/content/sites/wcchd/2022cha/2022WilliamsonTXCHA_FINAL.pdf), which lists heart disease as the county’s leading cause of death in 2020. This historical finding motivates the project; it does not establish screening performance.')

    st.subheader('From circulation to a camera signal')
    st.write('The right heart pumps blood toward the lungs. The left heart pumps oxygen-rich blood through the aorta. Fingertip photoplethysmography records changing light intensity associated with local pulsatile blood volume. Pressure, motion, temperature and camera exposure affect the recorded contour.')
    st.markdown('Anatomy reference: [NIH / NHLBI — Blood flow through the heart](https://www.nhlbi.nih.gov/health/heart/blood-flow). The Heart Explorer uses source-mapped anatomical reference meshes for its chambers, valves and coronary vessels.')

    st.subheader('Acquisition protocol')
    st.write('Record 20–25 seconds. The first 2 seconds and final 1 second of the processed segment are removed. Under 12 seconds is rejected; 12 to under 20 seconds requires approval. Decoding is capped at 25 seconds. The waveform and accepted-beat count determine whether features can be reported.')
    render_protocol()
    st.markdown('Contact-pressure evidence: [Teng & Zhang, 2004](https://doi.org/10.1088/0967-3334/25/5/020). Mean brightness is used as a recording-quality check; it does not measure finger pressure or identify capillary blanching.')

    st.subheader('Signal processing')
    st.write('OpenCV computes the full-frame mean red intensity. Shape-preserving PCHIP interpolation creates a uniform 200 Hz grid. A fourth-order Butterworth prototype, represented as second-order sections, is applied forward and backward over 0.5–8.5 Hz. A 15-sample quadratic Savitzky–Golay fit estimates VPG and APG derivatives.')
    st.write('PCHIP is C¹ continuous. The 200 Hz grid supports numerical processing; camera sampling still sets the captured temporal detail. Forward/backward filtering has zero phase shift and processes a recorded segment. A separate 0.35-second moving-mean detrended trace is available for inspection.')
    st.markdown('Implementation references: [PCHIP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html), [SOS filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html) and [Savitzky–Golay derivatives](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html).')

    st.subheader('Waveform features')
    st.latex(r'\mathrm{SI}=h/\Delta t\quad[\mathrm{m/s}],\qquad \mathrm{RI}=100\frac{A_{\mathrm{secondary}}-A_{\mathrm{foot}}}{A_{\mathrm{systolic}}-A_{\mathrm{foot}}}\quad[\%]')
    st.write('SI divides entered height by the delay to a secondary landmark. RI compares secondary and systolic amplitudes relative to the preceding pulse foot. At least four repeatable beat segments and four secondary candidates are required. SI follows the height/delay formulation; it is not a direct pulse-transit velocity measurement.')
    st.write('Beat shape is compared with a median template after normalization to 100 points. Segments below 0.80 correlation are excluded. Timing must fall within the supported 40–160 BPM processing range with interval coefficient of variation at most 0.20. Secondary candidates are searched within 10%–55% of each cycle. Shoulder and APG b/a features remain candidates for evaluation against reference waveforms.')
    st.markdown('Physiological definitions: [Millasseau et al., 2002](https://pubmed.ncbi.nlm.nih.gov/12241535/) and [Takazawa et al., 1998](https://pubmed.ncbi.nlm.nih.gov/9719069/).')

    with st.expander('Validation status and interpretation'):
        st.write('Automated checks exercise known generated signals, video decoding, quality gates, input changes and interface behavior. The Architecture page reports a reproducible local signal-processing benchmark with its scope and machine details.')
        st.write('Independent reference recordings are still required to establish clinical screening accuracy, repeatability across phones and reliable physiological landmark identification. Synthetic tests and frequency analysis of the same camera signal do not provide independent clinical validation. Disease tiers, vascular age and blood pressure are not reported. ARTERIO has no established equivalence to ABI or other clinical tests.')
    st.caption('Research use. Clinical screening accuracy has not yet been established; these outputs should not guide medical decisions.')
