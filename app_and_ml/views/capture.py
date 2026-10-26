"""Recording guidance, duration consent and a reversible retake action."""
import streamlit as st

from services.recordings import inspect_recording
from signal_processing.capture_policy import duration_gate, duration_error
from views.acquisition import render_protocol



def reset_capture():
    st.session_state['capture_version'] = st.session_state.get('capture_version', 0) + 1
    for key in ['upload_id', 'capture_metadata', 'capture_error', 'short_override', 'analysis_result']:
        st.session_state.pop(key, None)
    st.session_state['telemetry_data'] = {}
    st.session_state['telemetry_computed'] = False
    st.session_state['capture_notice'] = True


def render_capture():
    st.markdown('''<div class="capture-guide"><div class="bento-label">BEFORE YOU RECORD</div>
<div class="capture-specs"><div><strong>1080p · 60 FPS</strong><span>720p / 30 FPS also supported</span></div><div><strong>20 seconds+</strong><span>Aim for 20–25 seconds, with the phone resting flat</span></div><div><strong>Light contact</strong><span>Cover the rear lens and adjacent light without pressing hard</span></div></div>
<p>Keep your hand supported and still. Lock exposure and focus if your camera allows it. Upload the original camera video. Stop if you feel discomfort or the phone becomes warm.</p></div>''', unsafe_allow_html=True)
    render_protocol()
    if st.session_state.pop('capture_notice', False):
        st.info('Ready for a new take. Record a fresh 20–25 second video, then upload the original file below.')
    version = st.session_state.get('capture_version', 0)
    uploaded = st.file_uploader('Upload your original fingertip video', type=['mp4', 'mov', 'avi'],
                                key=f'capture_video_{version}',
                                help='Original rear-camera video, preferably 1080p / 60 FPS, 20–25 seconds, with gentle contact.')
    analyze = False
    if uploaded is not None:
        upload_id = uploaded.file_id
        if st.session_state.get('upload_id') != upload_id:
            st.session_state.update(upload_id=upload_id, telemetry_computed=False, telemetry_data={}, short_override=False)
            st.session_state.pop('analysis_result', None)
            st.session_state.pop('capture_error', None)
            st.session_state.pop('capture_metadata', None)
            try:
                st.session_state['capture_metadata'] = inspect_recording(uploaded)
            except (ValueError, OSError) as error:
                st.session_state['capture_error'] = str(error)
        metadata = st.session_state.get('capture_metadata')
        error = st.session_state.get('capture_error')
        if error:
            st.error(error)
        confirmed = st.checkbox('This is the original fingertip camera video, not a screen recording.', key=f'capture_confirm_{version}_{upload_id}')
        st.number_input('Height (cm), used for the experimental height / delay index', min_value=50.0, max_value=250.0,
                                 value=175.0, step=1.0, key='capture_height_cm', help='Enter your measured height. SI scales directly with this value; it does not measure pulse transit velocity.')
        gate = duration_gate(metadata['duration']) if metadata else 'reject'
        if metadata:
            st.caption(f"Detected: {metadata['width']} × {metadata['height']} pixels · {metadata['fps']:.2f} FPS · {metadata['duration']:.1f}s. Settings and original-capture status cannot be verified from metadata alone.")
            if metadata['fps_fallback']:
                st.warning('Frame rate is missing; 30 FPS will be assumed. Re-export at a known frame rate for more reliable timing.')
            if gate == 'reject':
                st.error(duration_error(metadata['duration']))
            elif gate == 'hold':
                st.markdown(f'''<div class="warning-modal-card" role="alert"><h3>SHORT RECORDING · {metadata['duration']:.1f}s</h3><p>Aim for 20–25 seconds. The first 2 seconds and last 1 second are removed, and motion can reduce the usable window further. More complete beats help summarize beat-to-beat variation, including changes with breathing. This clip needs your explicit approval before analysis.</p><p>For a longer sample, use “Retake / replace video”.</p></div>''', unsafe_allow_html=True)
            elif metadata['duration'] > 25:
                st.info('Analysis uses only the first 25 seconds. The start and end trims apply to that segment.')
        left, right = st.columns([2, 1])
        with left:
            label = 'Proceed with reduced window (low confidence)' if gate == 'hold' else 'Analyze recording'
            analyze = st.button(label, disabled=not confirmed or gate == 'reject', width='stretch')
            if analyze:
                st.session_state['short_override'] = gate == 'hold'
        with right:
            st.button('Retake / replace video', on_click=reset_capture, width='stretch')
        st.caption('Retake clears this upload and its results. Record again in your phone’s camera app, then choose the new file.')
    elif st.session_state.get('telemetry_computed'):
        st.button('Retake / replace video', on_click=reset_capture)
    return uploaded, analyze
