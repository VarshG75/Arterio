"""
views/architecture.py — Technical Pipeline & DSP Benchmarks
"""
import streamlit as st

def render_architecture_view():
    st.markdown("""
<div class="page-transition">
    <div class="section-pill">04 / SYSTEM ARCHITECTURE</div>
    <div class="hero-title">Technical Pipeline.</div>
    <div class="hero-caption">Decoupled digital signal processing and machine learning inference architecture powering PulseForm.</div>
</div>
""", unsafe_allow_html=True)

    # Clean, Unindented HTML Pipeline Card
    st.markdown("""
<div class="bento-card" style="margin-bottom: 2rem;">
    <div class="bento-label" style="margin-bottom: 1.4rem;">DATA DECOMPOSITION PIPELINE</div>
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe; text-transform: uppercase;">STEP 01 // CAPTURE</span>
            <div style="font-size: 1.05rem; font-weight: 500; color: #ffffff; margin-top: 2px;">Optical Stream Ingestion</div>
            <div style="font-size: 0.82rem; color: #8a8a93;">Capillary bed illuminated via smartphone LED; recorded at 30–60 FPS.</div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: rgba(255,255,255,0.04); padding: 4px 10px; border-radius: 6px;">.mp4 / .mov</div>
    </div>
    <div style="text-align: center; color: #00f2fe; font-size: 1.1rem; margin: -6px 0 6px 0;">↓</div>
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe; text-transform: uppercase;">STEP 02 // EXTRACTION</span>
            <div style="font-size: 1.05rem; font-weight: 500; color: #ffffff; margin-top: 2px;">OpenCV Matrix Channel Slicing</div>
            <div style="font-size: 0.82rem; color: #8a8a93;">Isolates average red-channel pixel brightness fluctuations across time frames.</div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: rgba(255,255,255,0.04); padding: 4px 10px; border-radius: 6px;">100 Hz Signal</div>
    </div>
    <div style="text-align: center; color: #00f2fe; font-size: 1.1rem; margin: -6px 0 6px 0;">↓</div>
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe; text-transform: uppercase;">STEP 03 // DSP FILTERING</span>
            <div style="font-size: 1.05rem; font-weight: 500; color: #ffffff; margin-top: 2px;">Zero-Phase 3rd-Order Butterworth Filter</div>
            <div style="font-size: 0.82rem; color: #8a8a93;">Isolates 0.5–5.0 Hz cardiac band; eliminates breathing wander and hand tremor.</div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: rgba(255,255,255,0.04); padding: 4px 10px; border-radius: 6px;">SciPy filtfilt</div>
    </div>
    <div style="text-align: center; color: #00f2fe; font-size: 1.1rem; margin: -6px 0 6px 0;">↓</div>
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 16px 20px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00f2fe; text-transform: uppercase;">STEP 04 // FEATURE EXTRACTION & INFERENCE</span>
            <div style="font-size: 1.05rem; font-weight: 500; color: #ffffff; margin-top: 2px;">Peak Geometric Decomposition & Risk Classifier</div>
            <div style="font-size: 0.82rem; color: #8a8a93;">Calculates Stiffness Index (SI), Reflection Index (RI), and vascular compliance category.</div>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; background: rgba(255,255,255,0.04); padding: 4px 10px; border-radius: 6px;">Scikit-Learn</div>
    </div>
</div>
""", unsafe_allow_html=True)

    c_tech1, c_tech2 = st.columns(2)
    with c_tech1:
        st.markdown("""
<div class="bento-card">
    <div class="bento-label">DIGITAL SIGNAL PROCESSING (DSP)</div>
    <div class="bento-metric">12 ms</div>
    <div class="bento-subtext">End-to-end signal filtering and peak detection latency across 1,000 continuous time-series data points.</div>
</div>
""", unsafe_allow_html=True)
    with c_tech2:
        st.markdown("""
<div class="bento-card">
    <div class="bento-label">MODEL ARCHITECTURE</div>
    <div class="bento-metric">100 Trees</div>
    <div class="bento-subtext">Random Forest ensemble trained on validated hemodynamic features extracted from clinical cohorts.</div>
</div>
""", unsafe_allow_html=True)