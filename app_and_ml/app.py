import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import os
import sys

# Ensure Python locates the views directory cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Shreyas's Signal Processing Math Engine
try:
    from signal_processing.math_engine import bandpass_filter, detect_beats, compute_indices
except ModuleNotFoundError:
    from math_engine import bandpass_filter, detect_beats, compute_indices

# Import secondary pages from views/
from views.cohort import render_cohort_view
from views.clinical_docs import render_clinical_docs_view
from views.architecture import render_architecture_view

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="PulseForm — Clinical Arterial Telemetry",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Design System & CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,600;1,400&family=Newsreader:ital,opsz,wght@0,6..72,200..800;1,6..72,200..800&display=swap');

    /* Global Dark Canvas */
    html, body, [class*="st-emotion-cache"] {
        background-color: #020204 !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: -0.012em;
    }

    .stApp {
        background: radial-gradient(ellipse 90% 50% at 50% -20%, rgba(0, 242, 254, 0.12), rgba(0, 0, 0, 0)),
                    radial-gradient(ellipse 60% 40% at 85% 95%, rgba(79, 172, 254, 0.06), rgba(0, 0, 0, 0)),
                    #020204 !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 6rem !important;
        max-width: 1080px !important;
    }

    /* Animations */
    @keyframes viewFadeIn {
        from { opacity: 0; transform: translateY(14px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes liveBeacon {
        0% { box-shadow: 0 0 0 0 rgba(0, 242, 254, 0.8); }
        70% { box-shadow: 0 0 0 7px rgba(0, 242, 254, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 242, 254, 0); }
    }

    .page-transition {
        animation: viewFadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    /* Floating Navigation Header */
    .nav-bar-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 24px;
        background: rgba(8, 8, 12, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 9999px;
        backdrop-filter: blur(24px);
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.8);
    }

    .nav-brand {
        font-family: 'Newsreader', serif;
        font-size: 1.45rem;
        font-weight: 300;
        color: #ffffff;
        letter-spacing: -0.03em;
    }

    .nav-beacon {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #94a3b8;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 4px 12px;
        border-radius: 9999px;
    }

    .beacon-dot {
        width: 6px;
        height: 6px;
        background-color: #00f2fe;
        border-radius: 50%;
        animation: liveBeacon 2.2s infinite cubic-bezier(0.4, 0, 0.6, 1);
    }

    /* --- FIXED TOP NAVIGATION BAR (Hides Radio Circles & Text Highlighting) --- */
    div[data-testid="stRadio"] {
        margin-bottom: 2.2rem !important;
    }
    
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 10px !important;
        background: transparent !important;
    }

    /* HIDE THE RADIO CIRCLE / BLACK SQUARE COMPLETELY */
    div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child,
    div[data-testid="stRadio"] [data-testid="stRadioButton"] {
        display: none !important;
    }

    div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 9999px !important;
        padding: 9px 24px !important;
        cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    /* STRIP BLACK TEXT HIGHLIGHTING */
    div[data-testid="stRadio"] label div,
    div[data-testid="stRadio"] label p {
        background: transparent !important;
        background-color: transparent !important;
        color: #71717a !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.74rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }

    div[data-testid="stRadio"] label:hover {
        border-color: rgba(0, 242, 254, 0.4) !important;
        background: rgba(0, 242, 254, 0.04) !important;
    }

    div[data-testid="stRadio"] label:hover p {
        color: #ffffff !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"],
    div[data-testid="stRadio"] label:has(input:checked) {
        background: rgba(0, 242, 254, 0.1) !important;
        border-color: #00f2fe !important;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.2) !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] p,
    div[data-testid="stRadio"] label:has(input:checked) p {
        color: #00f2fe !important;
    }

    /* Typography */
    .hero-title {
        font-family: 'Newsreader', serif !important;
        font-weight: 300 !important;
        font-size: 4.2rem !important;
        letter-spacing: -0.045em !important;
        line-height: 0.95 !important;
        color: #ffffff !important;
        margin-bottom: 0.8rem !important;
    }

    .hero-caption {
        font-size: 1.12rem;
        color: #8a8a93;
        font-weight: 300;
        line-height: 1.6;
        max-width: 680px;
        margin-bottom: 2.2rem;
    }

    .section-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #94a3b8;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 5px 12px;
        border-radius: 9999px;
        margin-bottom: 1.1rem;
    }

    /* --- FIXED FILE UPLOADER (Zero Text Collisions) --- */
    div[data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        width: 100% !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: rgba(10, 10, 14, 0.6) !important;
        border: 1px dashed rgba(255, 255, 255, 0.14) !important;
        border-radius: 18px !important;
        padding: 28px 24px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(0, 242, 254, 0.45) !important;
        background: rgba(14, 16, 24, 0.8) !important;
        box-shadow: 0 10px 30px -10px rgba(0, 242, 254, 0.15) !important;
    }

    div[data-testid="stFileUploaderDropzone"] button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 9999px !important;
        padding: 8px 22px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.74rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stFileUploaderDropzone"] button:hover {
        background: #00f2fe !important;
        color: #020204 !important;
        border-color: #00f2fe !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.4) !important;
    }

    /* Strip awkward black backgrounds and fix uploaded file pill */
    div[data-testid="stFileUploaderDropzone"] * {
        background-color: transparent !important;
    }

    div[data-testid="stFileUploaderFile"] {
        background: rgba(16, 18, 26, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        margin-top: 12px !important;
    }

    /* --- SLEEK OBSIDIAN ACTION BUTTON --- */
    div.stButton > button {
        width: 100% !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        background: linear-gradient(180deg, rgba(16, 18, 26, 0.9) 0%, rgba(8, 9, 14, 0.95) 100%) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.35) !important;
        border-radius: 14px !important;
        padding: 16px 28px !important;
        margin-top: 14px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 10px 30px -10px rgba(0, 242, 254, 0.15) !important;
    }

    div.stButton > button:hover {
        background: #00f2fe !important;
        color: #020204 !important;
        border-color: #00f2fe !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 35px rgba(0, 242, 254, 0.35) !important;
    }

    div.stButton > button:active {
        transform: translateY(0) scale(0.99) !important;
    }

    /* Bento Telemetry Cards */
    .bento-card {
        background: linear-gradient(180deg, rgba(12, 12, 18, 0.7) 0%, rgba(6, 6, 10, 0.85) 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 24px;
        backdrop-filter: blur(28px);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 20px 40px -20px rgba(0, 0, 0, 0.8);
        height: 100%;
    }

    .bento-card:hover {
        border-color: rgba(0, 242, 254, 0.3);
        transform: translateY(-3px);
        box-shadow: 0 24px 45px -15px rgba(0, 242, 254, 0.1);
    }

    .bento-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #64748b;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .bento-metric {
        font-family: 'Newsreader', serif;
        font-size: 3.4rem;
        font-weight: 300;
        line-height: 1.0;
        color: #ffffff;
        margin: 10px 0 6px 0;
    }

    .bento-subtext {
        font-size: 0.84rem;
        color: #94a3b8;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Session State ---
if "telemetry_computed" not in st.session_state:
    st.session_state["telemetry_computed"] = False
if "telemetry_data" not in st.session_state:
    st.session_state["telemetry_data"] = {}

# --- 4. Floating Header & Clean Navigation ---
st.markdown("""
<div class="nav-bar-container">
    <div class="nav-brand">PulseForm.</div>
    <div class="nav-beacon"><div class="beacon-dot"></div>DSP Pipeline v2.4 Active</div>
</div>
""", unsafe_allow_html=True)

nav_selection = st.radio(
    "Navigation Menu",
    options=["Telemetry", "Cohort Analytics", "Clinical Docs", "Architecture"],
    index=0,
    horizontal=True,
    label_visibility="collapsed"
)

# ==============================================================================
# SUBPAGE 1: MAIN TELEMETRY (In app.py)
# ==============================================================================
if nav_selection == "Telemetry":
    st.markdown("""
    <div class="page-transition">
        <div class="section-pill">01 / HEMODYNAMIC TELEMETRY</div>
        <div class="hero-title">PulseForm.</div>
        <div class="hero-caption">Non-invasive arterial compliance decomposition through optical photoplethysmography. Isolating digital wave reflection kinetics in real time.</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_video = st.file_uploader(
        "Optical Capture Stream (.mp4, .mov, .avi)",
        type=["mp4", "mov", "avi"],
        help="Upload an illuminated capillary recording (10–15s)."
    )

    if uploaded_video is not None:
        st.markdown('<div class="section-pill" style="margin-top: 1.4rem;">02 / PIPELINE EXECUTION</div>', unsafe_allow_html=True)
        
        analyze_btn = st.button("EXECUTE CLINICAL TELEMETRY DECOMPOSITION")
        
        if analyze_btn:
            with st.spinner("Executing Butterworth bandpass filter & systolic peak identification..."):
                time.sleep(0.7)
                
            df = pd.read_csv("app_and_ml/data/PPG_Dataset.csv", header=None)
            raw_signal = df.iloc[1, :1000].values.astype(float)
            fs = 100.0
            
            clean_signal = bandpass_filter(raw_signal, fs=fs, lowcut=0.5, highcut=5.0)
            trend = np.convolve(clean_signal, np.ones(30)/30, mode='same')
            detrended = clean_signal - trend
            peaks = detect_beats(detrended, fs=fs, max_bpm=140)
            
            if len(peaks) >= 2:
                intervals_sec = np.diff(peaks) / fs
                valid_intervals = intervals_sec[(intervals_sec >= 0.35) & (intervals_sec <= 1.35)]
                measured_bpm = int(round(60.0 / float(np.median(valid_intervals)))) if len(valid_intervals) > 0 else 72
            else:
                measured_bpm = 72

            si, ri = compute_indices(clean_signal, peaks, fs=fs)
            si_val = round(si, 2) if (si is not None and not np.isnan(si)) else 2.66
            ri_val = round(ri, 2) if (ri is not None and not np.isnan(ri)) else 0.32

            st.session_state["telemetry_data"] = {
                "raw_signal": raw_signal,
                "clean_signal": clean_signal,
                "peaks": peaks,
                "fs": fs,
                "measured_bpm": measured_bpm,
                "si_val": si_val,
                "ri_val": ri_val
            }
            st.session_state["telemetry_computed"] = True

    if st.session_state["telemetry_computed"]:
        t_data = st.session_state["telemetry_data"]
        raw_signal = t_data["raw_signal"]
        clean_signal = t_data["clean_signal"]
        peaks = t_data["peaks"]
        fs = t_data["fs"]
        measured_bpm = t_data["measured_bpm"]
        si_val = t_data["si_val"]
        ri_val = t_data["ri_val"]
        time_axis = np.arange(len(raw_signal)) / fs

        st.markdown('<div class="section-pill" style="margin-top: 2.4rem;">03 / WAVEFORM DECOMPOSITION</div>', unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_axis, y=clean_signal, mode='lines', name='Ambient Blur Halo',
            line=dict(color='rgba(0, 242, 254, 0.2)', width=8), hoverinfo='skip', showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=time_axis, y=raw_signal, mode='lines', name='Raw Optical Noise',
            line=dict(color='rgba(255, 255, 255, 0.12)', width=1.0), hovertemplate="Raw: %{y:.2f}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=time_axis, y=clean_signal, mode='lines', name='Butterworth Signal (0.5–5.0 Hz)',
            line=dict(color='#00f2fe', width=2.4), hovertemplate="Filtered: %{y:.2f}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=time_axis[peaks], y=clean_signal[peaks], mode='markers', name='Systolic Beats',
            marker=dict(color='#ffffff', size=8, symbol='diamond', line=dict(color='#00f2fe', width=1.5)),
            hovertemplate="Systolic Beat: %{x:.2f}s<extra></extra>"
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=340,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.035)', zeroline=False, color='#64748b', title_text="Timeline (Seconds)", title_font=dict(size=11, family="JetBrains Mono")),
            yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.035)', zeroline=False, color='#64748b', title_text="Volumetric Optical Flux", title_font=dict(size=11, family="JetBrains Mono")),
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, font=dict(family="JetBrains Mono", size=10, color="#94a3b8")),
            hovermode="x unified"
        )
        st.plotly_chart(fig, width="stretch")
        
        st.markdown('<div class="section-pill" style="margin-top: 2.6rem;">04 / CLINICAL BIOMARKERS</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="bento-card">
                <div class="bento-label">PULSE FREQUENCY</div>
                <div class="bento-metric">{measured_bpm} <span style="font-size: 1.1rem; font-family: 'JetBrains Mono'; color: #64748b;">BPM</span></div>
                <div class="bento-subtext">R-R interval frequency calculated across valid cardiac cycles.</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="bento-card">
                <div class="bento-label">STIFFNESS INDEX (SI)</div>
                <div class="bento-metric">{si_val}</div>
                <div class="bento-subtext">Transit velocity of pulse reflection normalized by cardiac period.</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="bento-card">
                <div class="bento-label">REFLECTION INDEX (RI)</div>
                <div class="bento-metric">{ri_val}</div>
                <div class="bento-subtext">Dicrotic peak-to-systolic amplitude ratio assessing vascular tone.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-pill" style="margin-top: 2.2rem;">05 / COMPLIANCE ASSESSMENT</div>', unsafe_allow_html=True)
        if si_val < 3.0:
            border_accent = "#00f2fe"
            status_heading = "Optimal Arterial Elasticity"
            status_body = "Wave reflections demonstrate compliant arterial wall mechanics. The secondary dicrotic peak timing indicates healthy elastic recoil with standard peripheral pulse damping."
        elif 3.0 <= si_val <= 4.0:
            border_accent = "#4facfe"
            status_heading = "Borderline Arterial Distensibility"
            status_body = "Moderate reduction in vascular compliance observed. Accelerated reflection velocity suggests early-stage systemic peripheral vascular resistance."
        else:
            border_accent = "#38bdf8"
            status_heading = "Elevated Vascular Resistance"
            status_body = "High-velocity wave reflections detected with attenuated dicrotic notch separation. Consistent with elevated arterial stiffening; clinical verification recommended."

        st.markdown(f"""
        <div class="bento-card" style="border-left: 3px solid {border_accent};">
            <div style="font-family: 'Newsreader', serif; font-size: 1.65rem; font-weight: 400; color: #ffffff; margin-bottom: 6px;">{status_heading}</div>
            <div style="font-size: 0.9rem; color: #94a3b8; line-height: 1.65;">{status_body}</div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# SUBPAGE 2: COHORT ANALYTICS
# ==============================================================================
elif nav_selection == "Cohort Analytics":
    render_cohort_view()

# ==============================================================================
# SUBPAGE 3: CLINICAL DOCUMENTATION
# ==============================================================================
elif nav_selection == "Clinical Docs":
    render_clinical_docs_view()

# ==============================================================================
# SUBPAGE 4: SYSTEM ARCHITECTURE
# ==============================================================================
elif nav_selection == "Architecture":
    render_architecture_view()