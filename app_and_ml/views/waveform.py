"""Plot measured landmarks and explain one beat without changing reported indices."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

CYAN = '#00f2fe'


def _style(figure, *, height=420, milliseconds=False):
    figure.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=height, autosize=True, margin=dict(l=0, r=8, t=30, b=20),
        font=dict(family='Inter, sans-serif', size=13, color='#c7d1d8'),
        hovermode='x unified',
        xaxis=dict(title='Time within this beat (ms)' if milliseconds else 'Time in recording (seconds)',
                   gridcolor='rgba(255,255,255,0.05)', zeroline=False, automargin=True),
        yaxis=dict(title='Intensity above pulse foot' if milliseconds else 'Relative red intensity',
                   gridcolor='rgba(255,255,255,0.05)', zeroline=False, automargin=True),
        legend=dict(orientation='h', y=-.24, x=0, yanchor='top', font=dict(size=12)),
    )
    return figure


def measured_landmarks(data):
    """Pair each recorded secondary candidate with its actual peak and pulse foot."""
    peaks = np.asarray(data['beat_indices'], dtype=int)
    feet = np.asarray(data['feet_indices'], dtype=int)
    length = len(data['clean_wave_array'])
    landmarks = []
    for record in data.get('reflection_records', []):
        beat, secondary = int(record['beat']), int(record['reflection'])
        if not 0 <= beat < min(len(peaks), len(feet)) - 1:
            continue
        foot, primary, end = int(feet[beat]), int(peaks[beat]), int(feet[beat + 1])
        if 0 <= foot < primary < secondary < end <= length:
            landmarks.append(dict(record, foot=foot, primary=primary, secondary=secondary, end=end))
    return landmarks


def overview_figure(data):
    time = np.asarray(data['time_axis'])
    clean = np.asarray(data['clean_wave_array'])
    peaks = np.asarray(data['beat_indices'], dtype=int)
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=time, y=data['raw_wave_array'], mode='lines', name='Raw · centered',
                               line=dict(color='#69757e', width=1)))
    figure.add_trace(go.Scatter(x=time, y=clean, mode='lines', name='Filtered PPG',
                               line=dict(color='#e8edf0', width=2)))
    figure.add_trace(go.Scatter(x=time[peaks], y=clean[peaks], mode='markers', name='Primary peaks',
                               marker=dict(color=CYAN, size=7),
                               hovertemplate='Primary candidate: %{x:.3f}s<extra></extra>'))
    landmarks = measured_landmarks(data)
    if landmarks:
        feet = [record['foot'] for record in landmarks]
        secondary = [record['secondary'] for record in landmarks]
        figure.add_trace(go.Scatter(x=time[feet], y=clean[feet], mode='markers', name='Pulse feet',
                                   marker=dict(color='#b3c0ca', size=7, symbol='diamond'),
                                   hovertemplate='Pulse foot: %{x:.3f}s<extra></extra>'))
        figure.add_trace(go.Scatter(x=time[secondary], y=clean[secondary], mode='markers',
                                   name='Secondary candidates', customdata=[r['method'] for r in landmarks],
                                   marker=dict(color='#fff', size=8, line=dict(color=CYAN, width=1.5)),
                                   hovertemplate='Secondary %{customdata}: %{x:.3f}s<extra></extra>'))
    return _style(figure)


def beat_measurements(data, record):
    time = np.asarray(data['time_axis'])
    clean = np.asarray(data['clean_wave_array'])
    foot, primary, secondary = (record[key] for key in ('foot', 'primary', 'secondary'))
    delay = float(time[secondary] - time[primary])
    systolic = float(clean[primary] - clean[foot])
    reflected = float(clean[secondary] - clean[foot])
    return dict(delay=delay, systolic=systolic, secondary=reflected,
                si=float(data['height_m'] / delay), ri=100 * reflected / systolic)


def beat_figure(data, record):
    clean = np.asarray(data['clean_wave_array'])
    time = np.asarray(data['time_axis'])
    foot, end = record['foot'], record['end']
    x = (time - time[foot]) * 1000
    y = clean - clean[foot]
    values = beat_measurements(data, record)
    primary_x, secondary_x = float(x[record['primary']]), float(x[record['secondary']])
    figure = go.Figure(go.Scatter(x=x[foot:end], y=y[foot:end], mode='lines', name='Selected beat',
                                 line=dict(color='#ecf4f6', width=2.5)))
    figure.add_hline(y=0, line_color='#7d8c96', line_dash='dot')
    figure.add_vrect(x0=primary_x, x1=secondary_x, fillcolor=CYAN, opacity=.08, line_width=0)
    for key, label, color, symbol in [('foot', 'Pulse foot', '#b3c0ca', 'diamond'),
                                       ('primary', 'Primary peak', CYAN, 'circle'),
                                       ('secondary', 'Secondary candidate', '#fff', 'circle')]:
        index = record[key]
        figure.add_trace(go.Scatter(x=[x[index]], y=[y[index]], mode='markers', name=label,
                                    marker=dict(color=color, size=10, symbol=symbol,
                                                line=dict(color=CYAN if key == 'secondary' else color, width=1.5)),
                                    hovertemplate=f'{label}: %{{x:.1f}} ms · %{{y:.3f}}<extra></extra>'))
    figure.add_annotation(x=(primary_x + secondary_x) / 2, y=1.12, yref='paper', showarrow=False,
                          text=f"Δt = {values['delay'] * 1000:.0f} ms", font=dict(color=CYAN, size=14))
    return _style(figure, height=410, milliseconds=True)


def render_beat_inspector(data):
    landmarks = measured_landmarks(data)
    if not landmarks or data['stiffness_index'] is None or data['reflection_index'] is None:
        st.caption('A beat inspector appears when enough repeatable secondary candidates pass the reporting checks. Missing SI/RI values remain withheld.')
        return
    st.subheader('See how this beat was measured')
    st.write('The cards above show medians across eligible beats. Select one beat below to inspect its own landmarks and calculation.')
    default = min(range(len(landmarks)), key=lambda i: abs(landmarks[i]['si'] - data['stiffness_index']))
    selected = st.selectbox('Inspect a measured beat', range(len(landmarks)), index=default,
                            format_func=lambda i: f"Beat {landmarks[i]['beat'] + 1} · {landmarks[i]['delay'] * 1000:.0f} ms · {'shoulder candidate' if landmarks[i]['method'] == 'shoulder' else 'secondary peak'}")
    record = landmarks[selected]
    st.plotly_chart(beat_figure(data, record), width='stretch', config={'displaylogo': False, 'responsive': True})
    values = beat_measurements(data, record)
    with st.container(key='beat_calculations'):
        st.markdown(f"**SI for this beat:** {data['height_m']:.2f} m ÷ {values['delay']:.3f} s = **{values['si']:.2f} m/s**")
        st.markdown(f"**RI for this beat:** 100 × {values['secondary']:.3f} ÷ {values['systolic']:.3f} = **{values['ri']:.1f}%**")
        st.caption('Both amplitudes are measured above the same pulse foot (the dotted baseline). The shaded interval is the primary-to-secondary delay. A secondary landmark is a waveform candidate, not proof of a reflected pressure wave.')
