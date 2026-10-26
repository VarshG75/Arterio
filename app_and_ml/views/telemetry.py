"""Upload workflow and measured waveform results."""
from pathlib import Path
from time import perf_counter
import streamlit as st

from services.recordings import analyze_recording
from views.capture import render_capture
from views.waveform import overview_figure, render_beat_inspector

STYLES = Path(__file__).resolve().parents[1] / 'assets/telemetry/telemetry.css'


def _metric(value, places=2):
    return '—' if value is None else f'{value:.{places}f}'


def render_results(data):
    duration = data['recorded_duration']
    if data['is_short_duration']:
        st.markdown(f'<div class="red-orange-pill-badge"><span>⚠</span> REDUCED SAMPLE WINDOW · {duration:.1f}s RECORDING · 20s+ RECOMMENDED</div>', unsafe_allow_html=True)
        st.caption('A shorter recording provides fewer complete beat segments. Review the waveform and repeatability indicators before interpreting the measurements.')
    else:
        st.markdown('<div class="section-pill">● 20S+ RECORDING ACQUIRED // 200 HZ PROCESSING GRID</div>', unsafe_allow_html=True)
    for warning in data['warnings']:
        st.warning(warning)
    if data['quality'] == 'partial':
        st.info(data['message'])
    st.plotly_chart(overview_figure(data), width='stretch', key='telemetry_overview',
                    config={'displaylogo': False, 'responsive': True})
    columns = st.columns(3)
    entries = [('PULSE RATE', _metric(data['heart_rate_bpm'], 0), 'BPM', 'Estimated from median optical peak intervals.'),
               ('STIFFNESS INDEX · SI', _metric(data['stiffness_index']), 'm/s', f"Height {data['height_m'] * 100:.0f} cm divided by the secondary-landmark delay."),
               ('REFLECTION INDEX · RI', _metric(data['reflection_index'], 1), '%', 'Secondary-to-systolic amplitude ratio, measured from the pulse foot.')]
    for column, (label, value, unit, note) in zip(columns, entries):
        with column:
            st.markdown(f'<div class="bento-card"><div class="bento-label">{label}</div><div class="bento-metric">{value} <small>{unit}</small></div><div class="bento-subtext">{note}</div></div>', unsafe_allow_html=True)
    st.caption(f"{data['accepted_beats']} repeatable beat segments · {data['reflection_beats']} secondary-landmark candidates · median template correlation {data['sqi_score']:.2f}. Correlation is a shape-consistency score, not diagnostic confidence.")
    render_beat_inspector(data)
    with st.expander('Signal processing details'):
        st.write(f"Start trim: 2.0s · End trim: 1.0s · Processed segment: {data['processed_duration']:.1f}s · Height: {data['height_m'] * 100:.0f} cm")
        st.write('PCHIP at 200 Hz → fourth-order Butterworth prototype in SOS form → forward/backward filtering → Savitzky–Golay derivatives. The moving-average detrended trace is available separately; landmarks use the bandpassed contour to avoid treating detrending artifacts as peaks.')
        if data.get('interval_cv') is not None:
            st.caption(f"Pulse-interval coefficient of variation: {data['interval_cv']:.3f}; processing limit 0.200.")
        st.caption(f"Signal processing time: {data['latency_ms']:.2f} ms on this run, excluding video decoding. APG b/a candidate: {_metric(data['ba_ratio'])}. No vascular age or disease tier is inferred.")
    st.caption('Research use. Clinical screening accuracy has not yet been established. These waveform indices do not provide a diagnosis or blood-pressure reading.')


def render_telemetry_view():
    st.html('<style>' + STYLES.read_text() + '</style>')
    st.markdown('''<div class="page-transition"><div class="section-pill">OPTICAL PULSE TELEMETRY</div><div class="hero-title">ARTERIO.</div><div class="hero-caption">Explore optical pulse waveforms from smartphone video, then discover the anatomy behind the signal.</div></div>''', unsafe_allow_html=True)
    uploaded, analyze = render_capture()
    if uploaded is not None and analyze:
        st.session_state.update(telemetry_computed=False, telemetry_data={})
        started = perf_counter()
        with st.container(key='telemetry_progress'):
            bar = st.progress(0.0, text='Preparing the recording')
            elapsed = st.empty()
            def report(value, message):
                bar.progress(min(1.0, max(0.0, value)), text=message)
                elapsed.caption(f'Elapsed {perf_counter() - started:.1f}s · Progress follows decoded frames and completed processing stages.')
            try:
                result = analyze_recording(uploaded, allow_short=st.session_state.get('short_override', False),
                                           height_m=st.session_state['capture_height_cm'] / 100, progress=report)
            except (ValueError, OSError) as error:
                result = dict(quality='error', message=str(error))
            if result['quality'] in ('good', 'partial'):
                bar.progress(1.0, text='Waveform ready' if result['quality'] == 'good' else 'Waveform ready · some indices are unavailable')
                elapsed.caption(f'Completed in {perf_counter() - started:.1f}s, including video decoding and signal analysis.')
            else:
                bar.empty()
                elapsed.caption(f'Processing stopped after {perf_counter() - started:.1f}s.')
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
