"""ARTERIO's local dashboard entry point."""
from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from styles import inject_editorial_theme
from views.opening import render_opening
from views.navigation import PAGES, initialize_page, remember_page
from views.telemetry import render_telemetry_view
from views.heart import render_heart_view
from views.cohort import render_cohort_view
from views.clinical_docs import render_clinical_docs_view
from views.architecture import render_architecture_view

st.set_page_config(page_title='ARTERIO — Vascular Screening', page_icon='🫀',
                   layout='wide', initial_sidebar_state='collapsed')
inject_editorial_theme()
initialize_page()
st.session_state.setdefault('telemetry_computed', False)
st.session_state.setdefault('telemetry_data', {})

with st.container(key='site_navigation'):
    st.markdown('''<div class="nav-bar-container"><button class="nav-brand" data-replay-intro type="button" title="Replay page opening" aria-label="Replay page opening">ARTERIO.</button><div class="nav-beacon"><div class="beacon-dot"></div>Vascular Screening</div></div>''', unsafe_allow_html=True)
    selected = st.radio('Navigation Menu', options=list(PAGES), key='active_page',
                        horizontal=True, width='stretch', label_visibility='collapsed')

remember_page(selected)

VIEWS = {'Telemetry': render_telemetry_view, 'Heart Explorer': render_heart_view,
         'Cohort Analytics': render_cohort_view, 'Clinical Docs': render_clinical_docs_view,
         'Architecture': render_architecture_view}
with st.container(key=f'page_{PAGES[selected]}'):
    VIEWS[selected]()
render_opening(selected)
