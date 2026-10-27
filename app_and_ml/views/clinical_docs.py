"""A readable overview with expandable methods, sources and validation status."""
from pathlib import Path

import streamlit as st
from views.acquisition import render_protocol

STYLES = Path(__file__).resolve().parents[1] / 'assets/clinical/reading.css'


def render_clinical_docs_view():
    st.html('<style>' + STYLES.read_text() + '</style>')
    st.markdown('<div class="section-pill">03 / SCIENCE & METHODS</div><div class="hero-title">From video to pulse.</div>', unsafe_allow_html=True)
    st.html('''<p class="clinical-lead">From light at your fingertip to the shape of a pulse. Understand what we capture, how we process it, and what the measurements mean.</p>
<ol class="clinical-flow" aria-label="From recording to interpretation">
<li><span>01 / CAPTURE</span><h2>Light becomes data.</h2><p>A rear-camera recording with the video light ON captures changing brightness at the fingertip.</p></li>
<li><span>02 / PROCESS</span><h2>Find a repeatable pulse.</h2><p>We filter the optical trace, compare beat shapes and locate candidate landmarks.</p></li>
<li><span>03 / INTERPRET</span><h2>Show the measurements.</h2><p>SI relates height to a landmark delay. RI compares amplitudes above the pulse foot. Missing landmarks stay missing.</p></li>
</ol>''')

    st.subheader('Why this problem matters')
    st.write('Accessible vascular screening is our long-term goal. The current application measures optical pulse features and helps explain the physiology behind them.')
    st.markdown('We identified a relevant local source: the [2022 Williamson County Community Health Assessment](https://www.healthywilliamsoncounty.org/content/sites/wcchd/2022cha/2022WilliamsonTXCHA_FINAL.pdf), which lists heart disease as the county’s leading cause of death in 2020. This historical finding motivates the project; it does not establish screening performance.')

    st.subheader('What the camera sees')
    st.write('The right heart pumps blood toward the lungs. The left heart pumps oxygen-rich blood through the aorta. Fingertip photoplethysmography records changing light intensity associated with local pulsatile blood volume. It does not image the heart.')
    st.write('Pressure, motion, temperature and automatic camera adjustments affect the contour. A steady recording and repeatable beats are essential to interpreting its features.')
    st.markdown('[Explore circulation with NIH / NHLBI](https://www.nhlbi.nih.gov/health/heart/blood-flow), or open Heart Explorer for the interactive anatomy.')

    st.subheader('Before you record')
    st.write('Turn the rear flash/video light ON for the full recording—not Auto or Off. Record 20–25 seconds with light contact and the phone supported. Turn AE/AF lock ON, if supported, so brightness and focus stay fixed.')
    render_protocol()
    with st.expander('Why contact and camera settings matter'):
        st.write('We remove the first 2 seconds and final 1 second. Stability checks then flag abrupt brightness changes, clipping, flat sections, high-frequency noise and timing gaps. Each flagged section gets a 1-second margin. The longest continuous section is selected before filtering; at least 8 seconds must remain. Separate sections are never joined. These thresholds are engineering choices and cannot identify every artifact.')
        st.write('Uploads under 12 seconds are rejected; 12 to under 20 seconds require approval. Only the first 25 seconds are decoded. The beat-shape and timing checks still apply to the selected section, and measurements stay blank if they fail.')
        st.markdown('Background on pulse-quality checks: [pulse morphology quality assessment](https://pubmed.ncbi.nlm.nih.gov/29059824/). That study supports checking waveform quality; it does not validate our thresholds or phone-camera implementation.')
        st.markdown('Contact-pressure evidence: [Teng & Zhang, 2004](https://doi.org/10.1088/0967-3334/25/5/020). Brightness is a recording-quality check; it does not measure pressure or identify capillary blanching.')
        st.markdown('Camera controls: [Apple — focus and exposure lock](https://support.apple.com/guide/iphone/use-camera-tools-iph3dc593597/ios). Other camera apps use different controls. The uploaded file cannot verify that the light or locks were enabled.')

    with st.expander('How we process the waveform'):
        st.write('OpenCV computes the full-frame mean red intensity. Shape-preserving PCHIP interpolation creates a uniform 200 Hz grid. A fourth-order Butterworth prototype, represented as second-order sections, is applied forward and backward over 0.5–8.5 Hz. A 15-point quadratic Savitzky–Golay fit estimates VPG and APG derivatives.')
        st.write('PCHIP is C¹ continuous. The 200 Hz grid supports numerical processing; camera sampling still sets the captured temporal detail. Forward/backward filtering has zero phase shift and processes a recorded segment. A separate 0.35-second moving-mean detrended trace is available for inspection.')
        st.markdown('Implementation references: [PCHIP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html), [SOS filtering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html) and [Savitzky–Golay derivatives](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html). Architecture shows the complete pipeline and scoped local benchmark.')

    with st.expander('What SI and RI measure'):
        st.latex(r'\mathrm{SI}=h/\Delta t\quad[\mathrm{m/s}]')
        st.latex(r'\mathrm{RI}=100\frac{A_{\mathrm{secondary}}-A_{\mathrm{foot}}}{A_{\mathrm{systolic}}-A_{\mathrm{foot}}}\quad[\%]')
        st.write('SI divides entered height by the delay to a secondary landmark. RI compares secondary and systolic amplitudes relative to the preceding pulse foot. At least four repeatable beat segments and four secondary candidates are required. SI follows the height/delay formulation; it is not a direct pulse-transit velocity measurement.')
        st.write('Beats are normalized to 100 points and compared with a median template. Segments below 0.80 correlation are excluded. Timing must lie within the supported 40–160 BPM processing range with interval coefficient of variation at most 0.20. Secondary candidates are searched within 10%–55% of each cycle. These checks measure consistency, not diagnostic confidence.')
        st.markdown('Physiological definitions: [digital-pulse SI study](https://pubmed.ncbi.nlm.nih.gov/12241535/) and [acceleration-plethysmogram study](https://pubmed.ncbi.nlm.nih.gov/9719069/). Their results do not validate this phone-camera pipeline.')

    with st.expander('Validation status and interpretation'):
        st.write('Automated checks exercise generated signals, video decoding, quality gates, input changes and interface behavior. The Architecture page reports a reproducible local signal-processing benchmark with its input and machine details.')
        st.write('Independent reference recordings are still required to establish clinical screening accuracy, repeatability across phones and reliable physiological landmark identification. Synthetic tests and frequency analysis of the same optical signal do not provide independent clinical validation. Disease tiers, vascular age and blood pressure are not reported. ARTERIO has no established equivalence to ABI or other clinical tests.')
    st.caption('Research use. Clinical screening accuracy has not yet been established; these outputs should not guide medical decisions.')
