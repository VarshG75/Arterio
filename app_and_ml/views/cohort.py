"""
views/cohort.py — Population Trends & Cohort Analytics
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go

def render_cohort_view():
    st.markdown("""
    <div class="page-transition">
        <div class="section-pill">02 / SIMULATED ILLUSTRATION</div>
        <div class="hero-title">Cohort Trends.</div>
        <div class="hero-caption">Illustrative simulation of how arterial stiffness is expected to rise with age. Simulated data, not real patient records.</div>
    </div>
    """, unsafe_allow_html=True)

    np.random.seed(42)
    cohort_ages = np.random.normal(54, 16, 800).clip(18, 92)
    cohort_si = 1.4 + 0.04 * cohort_ages + np.random.normal(0, 0.45, 800)

    fig_cohort = go.Figure()
    fig_cohort.add_trace(go.Scatter(
        x=cohort_ages,
        y=cohort_si,
        mode='markers',
        marker=dict(
            color=cohort_si,
            colorscale=[[0, '#00f2fe'], [0.5, '#4facfe'], [1, '#ffffff']],
            size=6,
            opacity=0.7,
            showscale=True,
            colorbar=dict(
                title=dict(text="SI", font=dict(family="JetBrains Mono", color="#94a3b8")),
                tickfont=dict(color="#94a3b8")
            )
        ),
        hovertemplate="Age: %{x:.0f} | SI: %{y:.2f}<extra></extra>"
    ))

    fig_cohort.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=380,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.035)',
            color='#64748b',
            title_text="Patient Age (Years)",
            title_font=dict(size=11, family="JetBrains Mono")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.035)',
            color='#64748b',
            title_text="Measured Stiffness Index (SI)",
            title_font=dict(size=11, family="JetBrains Mono")
        )
    )
    st.plotly_chart(fig_cohort, width="stretch")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="bento-card">
            <div class="bento-label">ABOUT THIS CHART</div>
            <div class="bento-metric">Simulated</div>
            <div class="bento-subtext">Generated from an assumed age-stiffness trend plus random noise. It shows the pattern PulseForm would be tested for, not measured results.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="bento-card">
            <div class="bento-label">POINTS PLOTTED</div>
            <div class="bento-metric">800</div>
            <div class="bento-subtext">Simulated points. Validation on real recorded finger videos is future work.</div>
        </div>
        """, unsafe_allow_html=True)