"""Recording guidance shared by Telemetry and Clinical Docs."""
import streamlit as st

PROTOCOL = [
    ('Flash / video light ON — required', 'In your rear camera’s Video mode, set the flash/video light to ON, not Auto or Off. It must stay lit for the entire 20–25 second recording. Cover the lens and adjacent light with your finger pad. This continuous illumination is required for ARTERIO’s fingertip recording protocol.'),
    ('Support your arms', 'Rest the phone and your hand on a table. Start recording, then gently cover the rear camera lens and adjacent light with your fingertip. The first 2 seconds are always removed. If you take longer to settle, the stability checks can leave out more of the recording.'),
    ('Use light, steady contact', 'Cover the lens and adjacent light with the finger pad. Let the finger rest without pressing hard. Excess pressure can alter local blood flow; a loose seal can admit ambient light or allow bouncing.'),
    ('AE/AF lock ON — hold brightness and focus steady', 'AE means auto exposure (brightness); AF means autofocus. After the finger is in place and the preview settles, turn the AE/AF LOCK ON if your camera supports it. The lock stops automatic readjustment; it does not turn the flash off. Keep it locked throughout the clip. On iPhone, touch and hold the preview until “AE/AF Lock” appears. Android camera controls vary: look for an AE/AF lock or manual exposure/focus setting. The uploaded file cannot confirm these settings.'),
    ('Keep hands comfortably warm', 'Use room-temperature or comfortably warm hands. Cold fingers can reduce the pulse signal. Stop if the phone or fingertip becomes warm or uncomfortable; do not keep recording through discomfort.'),
    ('Choose a practical camera setting', 'Use 1080p or 720p at 60 FPS when available; 30 FPS is supported with coarser timing. Avoid 4K because it adds decoding work without being needed for a spatial brightness average. Upload the original file, not a screen recording.'),
]


def render_protocol():
    with st.expander('Recording guide'):
        st.write('Record 20–25 seconds. We remove the first 2 seconds and final 1 second, then select the longest continuous section that passes stability checks. At least 8 seconds must remain in one section. Separate sections are never joined.')
        for i, (title, body) in enumerate(PROTOCOL, 1):
            st.markdown(f'**{i}. {title}** — {body}')
        st.caption('At 60 BPM, the retained 17-second window contains about 17 cycles before quality rejection. The accepted beat count depends on motion, exposure and waveform consistency.')
