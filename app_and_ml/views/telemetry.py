"""Upload workflow and measured waveform results."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from services.recordings import analyze_recording
from views.capture import render_capture


def _metric(value, places=2):
    return '—' if value is None else f'{value:.{places}f}'


def render_results(data):
    duration = data['recorded_duration']
    if data['is_short_duration']:
        st.markdown(f'<div class="red-orange-pill-badge"><span>⚠</span> REDUCED SAMPLE WINDOW · {duration:.1f}s RECORDING · 20s+ RECOMMENDED</div>', unsafe_allow_html=True)
        st.caption('Fewer beats may remain after quality rejection. Statistical confidence intervals are not estimated by this prototype.')
    else:
        st.markdown('<div class="section-pill">● 20S+ RECORDING ACQUIRED // 200 HZ PROCESSING GRID</div>', unsafe_allow_html=True)
    for warning in data['warnings']:
        st.warning(warning)
    if data['quality'] == 'partial':
        st.info(data['message'])
    time_axis = np.asarray(data['time_axis'])
    raw, clean = np.asarray(data['raw_wave_array']), np.asarray(data['clean_wave_array'])
    peaks = np.asarray(data['beat_indices'], dtype=int)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_axis, y=raw, mode='lines', name='Mean red · centered',
                             line=dict(color='#646d75', width=1), hovertemplate='Raw: %{y:.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=time_axis, y=clean, mode='lines', name='SOS Butterworth · 0.5–8.5 Hz',
                             line=dict(color='#e8edf0', width=2), hovertemplate='Filtered: %{y:.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=time_axis[peaks], y=clean[peaks], mode='markers', name='Candidate systolic peaks',
                             marker=dict(color='#00f2fe', size=6), hovertemplate='Peak: %{x:.2f}s<extra></extra>'))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=360,
                       margin=dict(l=0, r=0, t=40, b=0), hovermode='x unified',
                       xaxis=dict(title='Processed time (seconds)', gridcolor='rgba(255,255,255,0.035)', zeroline=False, color='#99a3ac'),
                       yaxis=dict(title='Relative red intensity', gridcolor='rgba(255,255,255,0.035)', zeroline=False, color='#99a3ac'),
                       legend=dict(orientation='h', y=1.15, font=dict(size=11, color='#a5afb7')))
    st.plotly_chart(fig, width='stretch')
    columns = st.columns(3)
    entries = [('PULSE FREQUENCY', _metric(data['heart_rate_bpm'], 0), 'BPM', 'Estimated from median optical peak intervals.'),
               ('HEIGHT / DELAY INDEX', _metric(data['stiffness_index']), 'm/s', f"Experimental SI using height {data['height_m'] * 100:.0f} cm; not measured pulse wave velocity."),
               ('REFLECTION AMPLITUDE', _metric(data['reflection_index'], 1), '%', 'Experimental RI relative to the preceding pulse foot.')]
    for column, (label, value, unit, note) in zip(columns, entries):
        with column:
            st.markdown(f'<div class="bento-card"><div class="bento-label">{label}</div><div class="bento-metric">{value} <small>{unit}</small></div><div class="bento-subtext">{note}</div></div>', unsafe_allow_html=True)
    st.caption(f"{data['accepted_beats']} repeatable beat segments · {data['reflection_beats']} secondary-landmark candidates · median template correlation {data['sqi_score']:.2f}. Correlation is a shape-consistency score, not diagnostic confidence.")
    with st.expander('Signal processing details'):
        st.write(f"Start trim: 2.0s · End trim: 1.0s · Processed segment: {data['processed_duration']:.1f}s · Height: {data['height_m'] * 100:.0f} cm")
        st.write('PCHIP at 200 Hz → fourth-order Butterworth prototype in SOS form → forward/backward filtering → Savitzky–Golay derivatives. The moving-average detrended trace is available separately; landmarks use the bandpassed contour to avoid treating detrending artifacts as peaks.')
        if data.get('interval_cv') is not None:
            st.caption(f"Pulse-interval coefficient of variation: {data['interval_cv']:.3f}; processing limit 0.200.")
        st.caption(f"Signal processing time: {data['latency_ms']:.2f} ms on this run, excluding video decoding. APG b/a candidate: {_metric(data['ba_ratio'])}. No vascular age or disease tier is inferred.")
    st.info('Research waveform descriptors. Secondary peaks and shoulders may have several causes; this app has no validated clinical thresholds, diagnosis or blood-pressure output.')


def render_telemetry_view():
    st.markdown('''<div class="page-transition"><div class="section-pill">OPTICAL PULSE TELEMETRY</div><div class="hero-title">ARTERIO.</div><div class="hero-caption">Explore optical pulse waveforms from smartphone video, then discover the anatomy behind the signal.</div></div>''', unsafe_allow_html=True)
    uploaded, analyze = render_capture()
    if uploaded is not None and analyze:
        st.session_state.update(telemetry_computed=False, telemetry_data={})
        with st.spinner('Reading the recording and checking the pulse waveform…'):
            try:
                result = analyze_recording(uploaded, allow_short=st.session_state.get('short_override', False),
                                           height_m=st.session_state['capture_height_cm'] / 100)
            except (ValueError, OSError) as error:
                result = dict(quality='error', message=str(error))
        st.session_state['analysis_result'] = result
        if result['quality'] in ('good', 'partial'):
            st.session_state.update(telemetry_computed=True, telemetry_data=result)
        elif result['quality'] == 'hold':
            metadata = st.session_state['capture_metadata'].copy()
            metadata['duration'] = result['recorded_duration']
            st.session_state['capture_metadata'] = metadata
            st.rerun()
    result = st.session_state.get('analysis_result', {})
    if result.get('quality') == 'error':
        st.error(result['message'])
    if st.session_state.get('telemetry_computed'):
        if st.button('Clear measurement'):
            st.session_state.update(telemetry_computed=False, telemetry_data={})
            st.session_state.pop('analysis_result', None)
            st.rerun()
        render_results(st.session_state['telemetry_data'])
