"""
views/clinical_docs.py - Medical Background and local context
"""
import streamlit as st


def render_clinical_docs_view():
    st.markdown(
        '<div class="page-transition">'
        '<div class="section-pill">03 / BACKGROUND</div>'
        '<div class="hero-title">Medical Rationale.</div>'
        '<div class="hero-caption">The science behind optical photoplethysmography and why arterial stiffness matters.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="bento-card" style="margin-bottom: 1.5rem;">'
        '<div style="font-family: \'Newsreader\', serif; font-size: 1.8rem; color: #fff; margin-bottom: 8px;">Physiological Foundation of Arterial Stiffness</div>'
        '<div style="font-size: 0.92rem; color: #94a3b8; line-height: 1.7;">'
        'During ventricular systole, the left ventricle ejects blood into the ascending aorta, launching a high-pressure incident pulse wave. '
        'As this wave travels peripherally, impedance mismatches at arterial bifurcations generate a secondary <b>reflected wave</b> traveling back toward the heart.<br><br>'
        'In compliant vasculature, arteries expand to absorb energy, so the reflected wave returns later in the beat. '
        'In stiffer vasculature, pulse waves travel faster and the reflection returns earlier, which is what the Stiffness Index measures.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<div class="bento-card"><div class="bento-label">LOCAL CONTEXT</div>'
            '<div style="font-family: \'Newsreader\', serif; font-size: 1.35rem; color: #ffffff; margin: 8px 0;">Williamson County, Texas</div>'
            '<div class="bento-subtext">The 2022 Williamson County Community Health Assessment lists heart disease as the leading cause of death in the county (2020 data). '
            'Low-cost, easy-to-use tools for learning about heart health are worth exploring.</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="bento-card"><div class="bento-label">CLINICAL CONTEXT</div>'
            '<div style="font-family: \'Newsreader\', serif; font-size: 1.35rem; color: #ffffff; margin: 8px 0;">Not a Replacement for ABI</div>'
            '<div class="bento-subtext">Doctors use the Ankle-Brachial Index (ABI) to check for peripheral artery disease, using a blood-pressure cuff, a Doppler device and a trained clinician. '
            'PulseForm measures something different and is not equivalent to ABI or any clinical test.</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="bento-card" style="margin-top: 1.5rem;">'
        '<div class="bento-label">DISCLAIMER</div>'
        '<div class="bento-subtext">PulseForm is an educational project, not a medical device. It does not diagnose, treat or screen for any condition.</div></div>',
        unsafe_allow_html=True,
    )
