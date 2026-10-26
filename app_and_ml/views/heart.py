"""Full-window ARTERIO anatomy scene, with the site's own scroll and navigation."""
import base64
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'heart'


@st.cache_data(show_spinner=False)
def embedded_assets(model_bytes, reference_one, reference_two):
    return tuple(base64.b64encode(blob).decode('ascii') for blob in (model_bytes, reference_one, reference_two))


def render_heart_view():
    # Let this route share the site's scroll while the scene fills the viewport.
    st.markdown('''<style>
    .stMainBlockContainer:has(.st-key-heart_experience){max-width:none !important;padding:0 !important;min-height:300vh !important}
    .st-key-heart_experience iframe{position:fixed !important;inset:0 !important;width:100vw !important;height:100dvh !important;max-width:none !important;border:0 !important;border-radius:0 !important;z-index:1}
    .st-key-heart_experience{min-height:300vh !important;pointer-events:none}
    .st-key-heart_experience iframe{pointer-events:auto}
    </style>''', unsafe_allow_html=True)
    model, first, second = embedded_assets(
        (ASSETS / 'models' / 'heart.glb').read_bytes(),
        (ASSETS / 'references' / 'heart-diagram-en.svg').read_bytes(),
        (ASSETS / 'references' / 'heart-chambers-valves.svg').read_bytes(),
    )
    html = (ASSETS / 'index.html').read_text()
    html = html.replace('__MODEL_BASE64__', model)
    html = html.replace('__EXTRA_ANATOMY__', (ASSETS / 'models' / 'cardiac-extras.json').read_text())
    html = html.replace('__REFERENCE_ONE__', 'data:image/svg+xml;base64,' + first)
    html = html.replace('__REFERENCE_TWO__', 'data:image/svg+xml;base64,' + second)
    with st.container(key='heart_experience'):
        st.iframe(html, height=800, tab_index=0)
