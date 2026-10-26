"""Local SVG/CSS brand reveal; no remote animation dependencies."""
from pathlib import Path
import streamlit as st

ASSET=Path(__file__).resolve().parents[1] / 'assets/brand/opening.html'

def render_opening():
    # Install the local opening overlay in the parent document.
    st.html('<style>.st-key-brand_bootstrap{height:0!important;min-height:0!important;margin:0!important;overflow:hidden}</style>')
    with st.container(key='brand_bootstrap'):
        st.iframe(ASSET.read_text(),height=1,tab_index=-1)
