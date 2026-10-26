"""ARTERIO's local dashboard entry point."""
from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from styles import inject_editorial_theme
from views.opening import render_opening
from views.telemetry import render_telemetry_view
from views.heart import render_heart_view
from views.cohort import render_cohort_view
from views.clinical_docs import render_clinical_docs_view
from views.architecture import render_architecture_view

st.set_page_config(page_title='ARTERIO — Optical Pulse Research', page_icon='🫀',
                   layout='wide', initial_sidebar_state='collapsed')
inject_editorial_theme()
render_opening()
st.session_state.setdefault('telemetry_computed', False)
st.session_state.setdefault('telemetry_data', {})

with st.container(key='site_navigation'):
    st.markdown('''<div class="nav-bar-container"><button class="nav-brand" data-replay-intro type="button" title="Replay opening" aria-label="Replay ARTERIO opening">ARTERIO.</button><div class="nav-beacon"><div class="beacon-dot"></div>Research prototype</div></div>''', unsafe_allow_html=True)
    selected = st.radio('Navigation Menu', options=['Telemetry', 'Heart Explorer', 'Cohort Analytics', 'Clinical Docs', 'Architecture'],
                        index=0, horizontal=True, width='stretch', label_visibility='collapsed')

VIEWS = {'Telemetry': render_telemetry_view, 'Heart Explorer': render_heart_view,
         'Cohort Analytics': render_cohort_view, 'Clinical Docs': render_clinical_docs_view,
         'Architecture': render_architecture_view}
VIEWS[selected]()
