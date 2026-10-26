"""Recording guidance shared by Telemetry and Clinical Docs."""
import streamlit as st

PROTOCOL = [
    ('Rest the phone and hand', 'Place the phone flat on a table with the rear lens accessible. Rest your hand on the same surface. This reduces movement from holding the phone or arm in the air.'),
    ('Use light, steady contact', 'Cover the lens and adjacent light with the finger pad. Let the finger rest without pressing hard. Excess pressure can alter local blood flow; a loose seal can admit ambient light or allow bouncing.'),
    ('Lock exposure and focus', 'Lock AE/AF in your camera app if supported, and keep exposure fixed during recording. Automatic brightness or focus changes can distort the waveform. The uploaded file cannot confirm these settings.'),
    ('Keep hands comfortably warm', 'Use room-temperature or comfortably warm hands. Cold fingers can reduce the pulse signal. Stop if the phone or fingertip becomes warm or uncomfortable; do not keep recording through discomfort.'),
    ('Choose a practical camera setting', 'Use 1080p or 720p at 60 FPS when available; 30 FPS is supported with coarser timing. Avoid 4K because it adds decoding work without being needed for a spatial brightness average. Upload the original file, not a screen recording.'),
]


def render_protocol():
    with st.expander('Acquisition Protocol & Clinical Guidance'):
        st.write('Record 20–25 seconds. ARTERIO removes the first 2 seconds and final 1 second of the processed segment; a 20-second clip leaves about 17 seconds before signal-quality rejection.')
        for i, (title, body) in enumerate(PROTOCOL, 1):
            st.markdown(f'**{i}. {title}** — {body}')
        st.caption('At 60 BPM, the retained 17-second window contains about 17 cycles before quality rejection. The accepted beat count depends on motion, exposure and waveform consistency.')
