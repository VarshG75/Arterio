"""Page entrances and independent scroll positions, installed in the host page."""
import json
from pathlib import Path
import streamlit as st
from views.navigation import PAGES

ASSETS = Path(__file__).resolve().parents[1] / 'assets/brand'


def render_opening(selected):
    st.html('<style>.st-key-brand_bootstrap{height:0!important;min-height:0!important;margin:0!important;overflow:hidden}</style>')
    html = (ASSETS / 'opening.html').read_text()
    html = html.replace('__PAGE_CONFIG__', json.dumps({'page': PAGES[selected], 'pages': PAGES}))
    html = html.replace('__NAVIGATION_SCRIPT__', (ASSETS / 'navigation.js').read_text())
    with st.container(key='brand_bootstrap'):
        st.iframe(html, height=1, tab_index=-1)
