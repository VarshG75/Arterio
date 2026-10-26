"""Interactive exploration of explicitly simulated observations."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats
import streamlit as st


def simulation():
    rng = np.random.default_rng(42)
    age = rng.normal(54, 16, 800).clip(18, 95)
    q = 1.4 + .04 * age + rng.normal(0, .45, 800)
    return pd.DataFrame({'id': np.arange(1, 801), 'age': age, 'q': q,
                         'r': np.clip(.25 + .09 * q + rng.normal(0, .08, 800), 0, 1)})


def render_cohort_view():
    st.markdown('<div class="section-pill">02 / SIMULATED DATA STUDY</div><div class="hero-title">Explore the patterns.</div>', unsafe_allow_html=True)
    st.write('Explore 800 simulated observations. Q is a dimensionless simulation variable, separate from Telemetry’s SI in m/s; these data are not patient records.')
    age_col, bin_col, mode_col = st.columns([1, 1, 1.4])
    with age_col:
        ages = st.slider('Simulated age range', 18, 95, (18, 95))
    with bin_col:
        selected = st.selectbox('Timing-ratio filter', ['All values', 'Q < 3', '3 ≤ Q ≤ 4', 'Q > 4'])
    with mode_col:
        mode = st.selectbox('Explore a view', ['Age trend & confidence band', 'Timing / amplitude density', 'Decade distribution'])
    frame = simulation()
    frame = frame[frame.age.between(*ages)]
    if selected == 'Q < 3': frame = frame[frame.q < 3]
    elif selected == '3 ≤ Q ≤ 4': frame = frame[frame.q.between(3, 4)]
    elif selected == 'Q > 4': frame = frame[frame.q > 4]
    if len(frame) < 3:
        st.info('This slice has fewer than three observations. Widen the filters to explore a trend.')
        return
    fig = go.Figure()
    if mode == 'Age trend & confidence band':
        x, y = frame.age.to_numpy(), frame.q.to_numpy()
        fig.add_trace(go.Scatter(x=x, y=y, text=frame.id, mode='markers', name='Simulated observations', marker=dict(size=5, color='#a1a1a8', opacity=.55), hovertemplate='Simulated ID %{text}<br>Age %{x:.0f}<br>Q %{y:.2f}<extra></extra>'))
        if np.ptp(x) > 0:
            fit = stats.linregress(x, y)
            grid = np.linspace(x.min(), x.max(), 100)
            estimate = fit.intercept + fit.slope * grid
            residual = y - (fit.intercept + fit.slope * x)
            band = stats.t.ppf(.975, len(x)-2) * np.sqrt(np.sum(residual**2)/(len(x)-2)) * np.sqrt(1/len(x)+(grid-x.mean())**2/np.sum((x-x.mean())**2))
            fig.add_trace(go.Scatter(x=grid, y=estimate-band, line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=grid, y=estimate+band, fill='tonexty', fillcolor='rgba(230,230,235,.10)', line=dict(width=0), name='95% mean-response band', hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=grid, y=estimate, line=dict(color='white', width=2), name='Linear fit'))
        axes = ('Simulated age (years)', 'Simulated timing ratio Q (dimensionless)')
    elif mode == 'Timing / amplitude density':
        fig.add_trace(go.Histogram2dContour(x=frame.r, y=frame.q, colorscale=[[0, '#09090c'], [1, '#eeeeef']], contours=dict(coloring='heatmap'), colorbar=dict(title='Count')))
        axes = ('Simulated amplitude ratio R', 'Simulated timing ratio Q')
    else:
        fig.add_trace(go.Histogram(x=frame.age, xbins=dict(start=10, end=100, size=10), marker_color='#d4d4d8', name='Generated observations'))
        axes = ('Simulated age (decades)', 'Observation count')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=440, font=dict(color='#aaaab1'), margin=dict(l=10,r=10,t=20,b=10), xaxis=dict(title=axes[0], gridcolor='#222228'), yaxis=dict(title=axes[1], gridcolor='#222228'), legend=dict(orientation='h', y=1.15))
    st.plotly_chart(fig, width='stretch')
    corr = stats.pearsonr(frame.age, frame.q)
    cells = st.columns(4)
    cells[0].metric('Slice size', f'{len(frame):,}')
    cells[1].metric('Pearson r', f'{corr.statistic:.2f}')
    cells[2].metric('Median Q', f'{frame.q.median():.2f}')
    cells[3].metric('Q interquartile range', f'{frame.q.quantile(.75)-frame.q.quantile(.25):.2f}')
    st.caption(f'Pearson p = {corr.pvalue:.3g} for this simulated slice. The generating formula creates the relationship; this is not evidence about real vascular aging. Q bins are illustrative numeric filters, not clinical risk tiers.')
    with st.expander('Inspect the selected simulated records'):
        st.dataframe(frame.rename(columns={'id':'Simulation ID','q':'Timing ratio Q','r':'Amplitude ratio R','age':'Simulated age'}), hide_index=True, width='stretch')
