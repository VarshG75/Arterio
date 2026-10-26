"""Upload workflow and measured waveform results."""
from pathlib import Path
from time import perf_counter

import numpy as np
import streamlit as st

from services.recordings import analyze_recording
from views.capture import render_capture
from views.waveform import overview_figure, render_beat_inspector

STYLES = Path(__file__).resolve().parents[1] / 'assets/telemetry/telemetry.css'


def _metric(value, places=2):
    return '—' if value is None else f'{value:.{places}f}'


NOTICE_STYLES = {'error': st.error, 'warning': st.warning, 'info': st.info}
DISCLAIMER = ('SI and RI are experimental waveform-derived measurements. Their clinical accuracy has not been '
              'established, and they should not be used to diagnose cardiovascular disease.')


def render_notices(data):
    """Show specific quality notices; fall back to plain warnings for older results."""
    notices = data.get('notices')
    if notices is None:
        for warning in data.get('warnings', []):
            st.warning(warning)
        if data.get('quality') == 'partial':
            st.info(data['message'])
        return
    for notice in notices:
        text = f"**{notice['title']}** — {notice['body']}"
        if notice.get('next_step'):
            text += f"\n\n*Next time:* {notice['next_step']}"
        NOTICE_STYLES.get(notice['level'], st.info)(text)


def render_measurement_details(data, time_axis):
    """Compact view of the beats and secondary landmarks behind SI and RI."""
    records = data.get('reflection_records') or []
    with st.expander('Waveform Measurement Details'):
        methods = [r['method'] for r in records]
        cols = st.columns(4)
        cols[0].metric('Accepted pulse cycles', data.get('accepted_beats', 0))
        cols[1].metric('Secondary landmarks', data.get('reflection_beats', 0))
        cols[2].metric('Found as peak / shoulder', f"{methods.count('peak')} / {methods.count('shoulder')}")
        sqi = data.get('sqi_score')
        cols[3].metric('Beat shape consistency', '—' if sqi is None else f'{sqi:.2f}')
        st.caption('SI and RI need at least 4 accepted cycles and 4 secondary landmarks, with pulse timing that passes '
                   'the consistency check. A cycle is accepted when its shape correlates at least 0.80 with the median beat.')
        indicators = []
        if data.get('interval_cv') is not None:
            indicators.append(f"pulse-interval variation {data['interval_cv']:.1%} (limit 20%)")
        if data.get('motion_variance_ratio') is not None:
            indicators.append(f"abrupt-change score {data['motion_variance_ratio']:.1f} (caution above 4)")
        if data.get('mean_red') is not None:
            indicators.append(f"mean red brightness {data['mean_red']:.0f} (accepted range 30–250)")
        if data.get('analysis_window'):
            start, end = data['analysis_window']
            indicators.append(f'analyzed seconds {start:.0f}–{end:.0f} of the recording')
        if indicators:
            st.caption('Quality indicators: ' + ' · '.join(indicators) + '.')
        missing = data.get('missing_reasons') or {}
        labels = {'pulse': 'Pulse rate', 'si': 'SI', 'ri': 'RI'}
        for key, reason in missing.items():
            st.markdown(f"**{labels.get(key, key)} unavailable:** {reason}")
        if records and data.get('stiffness_index') is None:
            st.caption(f'{len(records)} secondary-landmark candidates were found, but they were not used because the '
                       'recording did not pass the checks above, so no per-cycle SI or RI values are listed.')
        elif records:
            rows = [{'Cycle': r['beat'] + 1,
                     'Time (s)': round(float(time_axis[r['reflection']]), 2) if r['reflection'] < len(time_axis) else None,
                     'Method': r['method'], 'Delay (ms)': round(r['delay'] * 1000),
                     'SI (m/s)': round(r['si'], 2), 'RI (%)': round(r['ri'], 1),
                     'Outside typical range': 'yes' if r.get('outside_reference_bounds') else ''}
                    for r in records]
            st.dataframe(rows, hide_index=True, width='stretch')
            st.caption('SI and RI on the cards are the medians of these per-cycle values. "Outside typical range" flags '
                       'values outside 4–18 m/s or 20–98 %; it describes the measurement, not your health.')
        else:
            st.caption('No secondary landmarks were measured in this recording.')


def render_results(data):
    duration = data['recorded_duration']
    if data['is_short_duration']:
        st.markdown(f'<div class="red-orange-pill-badge"><span>⚠</span> REDUCED SAMPLE WINDOW · {duration:.1f}s RECORDING · 20s+ RECOMMENDED</div>', unsafe_allow_html=True)
        st.caption('A shorter recording provides fewer complete beat segments. Review the waveform and repeatability indicators before interpreting the measurements.')
    else:
        st.markdown('<div class="section-pill">● 20S+ RECORDING ACQUIRED // 200 HZ PROCESSING GRID</div>', unsafe_allow_html=True)
    render_notices(data)
    time_axis = np.asarray(data['time_axis'])
    st.plotly_chart(overview_figure(data), width='stretch', key='telemetry_overview',
                    config={'displaylogo': False, 'responsive': True})
    columns = st.columns(3)
    missing = data.get('missing_reasons') or {}
    entries = [('PULSE RATE', _metric(data['heart_rate_bpm'], 0), 'BPM',
                missing.get('pulse', 'Estimated from median optical peak intervals.')),
               ('STIFFNESS INDEX · EXPERIMENTAL', _metric(data['stiffness_index']), 'm/s',
                missing.get('si', f"Height {data['height_m'] * 100:.0f} cm divided by the secondary-landmark delay.")),
               ('REFLECTION INDEX · EXPERIMENTAL', _metric(data['reflection_index'], 1), '%',
                missing.get('ri', 'Secondary-to-systolic amplitude ratio, measured from the pulse foot.'))]
    for column, (label, value, unit, note) in zip(columns, entries):
        with column:
            st.markdown(f'<div class="bento-card"><div class="bento-label">{label}</div><div class="bento-metric">{value} <small>{unit}</small></div><div class="bento-subtext">{note}</div></div>', unsafe_allow_html=True)
    st.caption(f"{data['accepted_beats']} repeatable beat segments · {data['reflection_beats']} secondary-landmark candidates · median template correlation {data['sqi_score']:.2f}. Correlation is a shape-consistency score, not diagnostic confidence.")
    render_beat_inspector(data)
    render_measurement_details(data, time_axis)
    with st.expander('Signal processing details'):
        st.write(f"Start trim: 2.0s · End trim: 1.0s · Processed segment: {data['processed_duration']:.1f}s · Height: {data['height_m'] * 100:.0f} cm")
        st.write('PCHIP at 200 Hz → fourth-order Butterworth prototype in SOS form → forward/backward filtering → Savitzky–Golay derivatives. The moving-average detrended trace is available separately; landmarks use the bandpassed contour to avoid treating detrending artifacts as peaks.')
        if data.get('interval_cv') is not None:
            st.caption(f"Pulse-interval coefficient of variation: {data['interval_cv']:.3f}; processing limit 0.200.")
        st.caption(f"Signal processing time: {data['latency_ms']:.2f} ms on this run, excluding video decoding. APG b/a candidate: {_metric(data['ba_ratio'])}. No vascular age or disease tier is inferred.")
    st.caption(DISCLAIMER + ' These waveform indices do not provide a diagnosis or blood-pressure reading.')


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
