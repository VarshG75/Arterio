"""Sources, capture guidance and the meaning of the experimental measurements."""
import streamlit as st
from views.acquisition import render_protocol


def render_clinical_docs_view():
    st.markdown('<div class="section-pill">03 / RESEARCH CONTEXT</div><div class="hero-title">Behind the pulse.</div>', unsafe_allow_html=True)
    st.write('ARTERIO explores optical pulse waveforms recorded with a smartphone camera. This page explains the recording protocol, the mathematics and the limits of the resulting measurements.')
    st.subheader('From heart contraction to an optical signal')
    st.write('The right heart pumps blood toward the lungs. The left heart pumps oxygen-rich blood through the aorta. A fingertip camera recording detects changing light intensity associated with local blood volume; it does not image the heart.')
    st.markdown('Anatomy: [NIH / NHLBI — Blood flow through the heart](https://www.nhlbi.nih.gov/health/heart/blood-flow). The atlas includes four chambers, four valve assemblies, major vessels and coronary vessels. Its source meshes remain simplified anatomical references.')

    st.subheader('The 20-second acquisition protocol')
    st.write('Aim for 20–25 seconds. Under 12 seconds is rejected; 12 to under 20 seconds requires explicit approval and carries a reduced-window warning. Analysis decodes at most 25 seconds and removes the first 2 seconds and final 1 second of that segment. At 60 BPM, a 20-second recording leaves about 17 cycles before beat-quality rejection, while 15 seconds leaves about 12.')
    st.write('Longer recordings provide more opportunities to compare repeated beats and observe breathing-related variation. Neither duration nor beat count guarantees stable vascular measurements. Twenty seconds is ARTERIO’s engineering target, not a universal clinical standard established by the papers below.')
    render_protocol()
    st.markdown('Contact-force context: [Teng & Zhang, 2004](https://doi.org/10.1088/0967-3334/25/5/020). Their experiment demonstrates that contact force affects PPG features; a phone’s mean red intensity cannot diagnose capillary blanching or measure contact pressure.')

    st.subheader('The processing sequence')
    st.write('OpenCV reduces each decoded frame to its mean red-channel intensity. PCHIP interpolation places the retained samples on a 200 Hz grid. A fourth-order Butterworth prototype is represented as second-order sections and applied forward and backward at 0.5–8.5 Hz. Savitzky–Golay fits estimate first and second derivatives with a 15-sample quadratic window.')
    st.write('PCHIP preserves local sample shape and is C¹ continuous, rather than C². Interpolation adds sample locations, not captured temporal detail. Forward/backward filtering requires the recorded segment and has zero phase shift; it still takes time to execute. A 0.35-second moving-mean detrended trace is available separately, while landmarks use the bandpassed contour.')
    st.markdown('Implementation references: [SciPy PCHIP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html), [SOS filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html), and [Savitzky–Golay derivatives](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html).')

    st.subheader('Indices and landmark quality')
    st.latex(r'\mathrm{SI}=h/\Delta t\quad[\mathrm{m/s}],\qquad \mathrm{RI}=100\frac{A_{\mathrm{secondary}}-A_{\mathrm{foot}}}{A_{\mathrm{systolic}}-A_{\mathrm{foot}}}\quad[\%]')
    st.write('Enter measured height in Telemetry. Height divided by the delay to a secondary landmark follows the dimensional definition of digital-pulse SI; it is not a measured pulse transit velocity. RI uses amplitudes relative to the preceding pulse foot. These outputs replace the earlier dimensionless cycle/delay ratio and zero-centered amplitude ratio; values from the two versions are not interchangeable.')
    st.write('Beats are normalized to 100 points and compared with a median template. Segments with correlation below 0.80 are excluded. At least four repeatable segments and four secondary-landmark candidates are required to report SI and RI. A 10%–55% search window limits candidate locations, but cannot prove that a feature is a reflected wave. A descending-slope shoulder is identified as a candidate, not a diagnosis. APG b/a candidates are exploratory; no vascular age is calculated.')
    st.markdown('Research definitions: [Millasseau et al., 2002](https://pubmed.ncbi.nlm.nih.gov/12241535/) and [Takazawa et al., 1998](https://pubmed.ncbi.nlm.nih.gov/9719069/). Their results do not validate ARTERIO’s camera pipeline, thresholds or shoulder detector.')
    st.subheader('Quality checks and interpretation')
    st.write('The app checks duration, mean brightness, near-flat signals, sudden frame-to-frame changes and repeated beat shape. A motion warning is a heuristic rather than a measured SNR. Template correlation measures consistency, not disease probability. Missing landmarks remain blank, and measured values are never clipped into an expected clinical range.')
    st.info('Research and education only. Clinical accuracy, PAD screening equivalence, blood-pressure estimation and regulatory clearance have not been established. A software self-test verifies code behavior on generated signals, not medical accuracy.')
