"""
views/architecture.py - Technical Pipeline
"""
import streamlit as st

_LABEL = "font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe; text-transform: uppercase;"
_TITLE = "font-size: 1.05rem; font-weight: 500; color: #ffffff; margin-top: 2px;"
_DESC = "font-size: 0.82rem; color: #8a8a93;"
_TAG = "font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: rgba(255,255,255,0.04); padding: 4px 10px; border-radius: 6px;"
_ROW = "background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 16px 20px; display: flex; align-items: center; justify-content: space-between;"


def _step(label, title, desc, tag, last=False):
    margin = "0" if last else "12px"
    html = (
        f'<div style="{_ROW} margin-bottom: {margin};">'
        f'<div><span style="{_LABEL}">{label}</span>'
        f'<div style="{_TITLE}">{title}</div>'
        f'<div style="{_DESC}">{desc}</div></div>'
        f'<div style="{_TAG}">{tag}</div></div>'
    )
    if not last:
        html += '<div style="text-align: center; color: #00f2fe; font-size: 1.1rem; margin: -6px 0 6px 0;">&darr;</div>'
    return html


def render_architecture_view():
    st.markdown(
        '<div class="page-transition">'
        '<div class="section-pill">04 / SYSTEM ARCHITECTURE</div>'
        '<div class="hero-title">Technical Pipeline.</div>'
        '<div class="hero-caption">How a phone video of a fingertip becomes a heart rate and stiffness measurement.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    steps = [
        _step("STEP 01 // CAPTURE", "Optical Stream Ingestion",
              "Fingertip over the camera and flash; the video is recorded at about 30 frames per second.", ".mp4 / .mov"),
        _step("STEP 02 // EXTRACTION", "Red-Channel Signal and Resampling",
              "Averages the red brightness of every frame, then resamples it to a uniform 100 Hz with a cubic spline.", "OpenCV + SciPy"),
        _step("STEP 03 // DSP FILTERING", "Zero-Phase 3rd-Order Butterworth Filter",
              "Keeps the 0.5 to 5.0 Hz cardiac band and removes breathing drift and hand tremor.", "SciPy filtfilt"),
        _step("STEP 04 // BEAT ANALYSIS", "Peak Detection and Reflection Analysis",
              "Finds each heartbeat, then measures the reflected-wave delay and height to compute the Stiffness Index (SI) and Reflection Index (RI).", "SciPy find_peaks"),
        _step("STEP 05 // QUALITY CHECK", "Signal-Quality Gate",
              "Rejects recordings with a weak or irregular pulse and asks for a re-recording instead of reporting a number.", "beat spacing check", last=True),
    ]
    st.markdown(
        '<div class="bento-card" style="margin-bottom: 2rem;">'
        '<div class="bento-label" style="margin-bottom: 1.2rem;">DATA DECOMPOSITION PIPELINE</div>'
        + "".join(steps) + '</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<div class="bento-card"><div class="bento-label">SAMPLING</div>'
            '<div class="bento-metric">100 Hz</div>'
            '<div class="bento-subtext">Every recording is resampled to a uniform 100 samples per second before filtering, because phone frame rates drift.</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="bento-card"><div class="bento-label">CARDIAC BAND</div>'
            '<div class="bento-metric">0.5-5 Hz</div>'
            '<div class="bento-subtext">A zero-phase Butterworth bandpass keeps heartbeat frequencies and removes slower and faster noise.</div></div>',
            unsafe_allow_html=True,
        )
