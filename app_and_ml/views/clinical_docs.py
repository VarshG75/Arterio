"""
views/clinical_docs.py — Medical Rationale & TX-31 Healthcare Context
"""
import streamlit as st

def render_clinical_docs_view():
    st.markdown("""
    <div class="page-transition">
        <div class="section-pill">03 / CLINICAL VALIDATION</div>
        <div class="hero-title">Medical Rationale.</div>
        <div class="hero-caption">Theoretical foundation of optical photoplethysmography and physiological relevance in Central Texas cardiovascular screening.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="bento-card" style="margin-bottom: 1.5rem;">
        <div style="font-family: 'Newsreader', serif; font-size: 1.8rem; color: #fff; margin-bottom: 8px;">Physiological Foundation of Arterial Stiffness</div>
        <div style="font-size: 0.92rem; color: #94a3b8; line-height: 1.7;">
            During ventricular systole, the left ventricle ejects blood into the ascending aorta, launching a high-pressure incident pulse wave. As this wave travels peripherally, impedance mismatches at arterial bifurcations generate a secondary <b>reflected wave</b> traveling retrograde back toward the heart.<br><br>
            In compliant vasculature, arteries dilate to absorb kinetic energy, delaying the reflected wave so it arrives during diastole. In stiffened or hypertensive vasculature, increased pulse wave velocity returns the reflection prematurely during systole, elevating cardiac afterload.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_doc1, c_doc2 = st.columns(2)
    with c_doc1:
        st.markdown("""
        <div class="bento-card">
            <div class="bento-label">LOCAL CLINICAL IMPERATIVE</div>
            <div style="font-family: 'Newsreader', serif; font-size: 1.35rem; color: #ffffff; margin: 8px 0;">Williamson County, Texas (TX-31)</div>
            <div class="bento-subtext">According to the Williamson County Community Health Assessment, heart disease remains the primary cause of mortality in the district. Rapid suburban expansion in Leander and Round Rock strains primary care clinic capacities, making zero-cost smartphone screening essential.</div>
        </div>
        """, unsafe_allow_html=True)
    with c_doc2:
        st.markdown("""
        <div class="bento-card">
            <div class="bento-label">CLINICAL BENCHMARK</div>
            <div style="font-family: 'Newsreader', serif; font-size: 1.35rem; color: #ffffff; margin: 8px 0;">Ankle-Brachial Index (ABI) Equivalence</div>
            <div class="bento-subtext">Standard clinical evaluation of peripheral artery disease requires Doppler ABI equipment ($2,500+) and trained technicians. PulseForm delivers an accessible surrogate screening metric via consumer optical sensors.</div>
        </div>
        """, unsafe_allow_html=True)