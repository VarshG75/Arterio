"""Page names and refresh-safe routing for the shared navigation bar."""
import streamlit as st

PAGES = {
    'Telemetry': 'telemetry',
    'Heart Explorer': 'heart-explorer',
    'Cohort Analytics': 'cohort',
    'Clinical Docs': 'clinical-docs',
    'Architecture': 'architecture',
}


def initialize_page():
    route = st.query_params.get('page', 'telemetry')
    if st.session_state.get('_route_param') != route:
        st.session_state['active_page'] = next(
            (name for name, slug in PAGES.items() if slug == route), 'Telemetry')


def remember_page(selected):
    route = PAGES[selected]
    if st.query_params.get('page') != route:
        st.query_params['page'] = route
    st.session_state['_route_param'] = route
