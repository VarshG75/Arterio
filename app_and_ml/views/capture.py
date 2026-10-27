"""Recording guidance, duration consent and a reversible retake action."""
import streamlit as st

from services.recordings import inspect_recording
from signal_processing.capture_policy import duration_gate, duration_error
from views.acquisition import render_protocol
from views.height import render_height_input



def invalidate_measurement():
    """Inputs changed; keep the upload but remove its previous analysis."""
    st.session_state['telemetry_computed'] = False
    st.session_state['telemetry_data'] = {}
    st.session_state.pop('analysis_result', None)


def upload_changed(key):
    """Handle explicit removal without clearing results merely on page navigation."""
    if st.session_state.get(key) is None:
        invalidate_measurement()
        for name in ('upload_id', 'capture_metadata', 'capture_error', 'short_override'):
            st.session_state.pop(name, None)


def reset_capture():
    st.session_state['capture_version'] = st.session_state.get('capture_version', 0) + 1
    for key in ['upload_id', 'capture_metadata', 'capture_error', 'short_override', 'analysis_result', 'capture_confirmation_attempted']:
        st.session_state.pop(key, None)
    st.session_state['telemetry_data'] = {}
    st.session_state['telemetry_computed'] = False
    st.session_state['capture_notice'] = True


def clear_confirmation_warning():
    st.session_state.pop('capture_confirmation_attempted', None)


def render_capture():
    st.markdown('''<div class="capture-guide"><div class="bento-label">BEFORE YOU RECORD</div>
<aside class="capture-flash-required"><strong>Flash / video light: ON <span>REQUIRED</span></strong><p>Use the rear camera in Video mode. Choose <b>ON</b>, not Auto or Off, and keep the light on for the entire recording.</p></aside>
<div class="capture-specs"><div><strong>1080p · 60 FPS</strong><span>720p / 30 FPS also supported</span></div><div><strong>20 seconds+</strong><span>Aim for 20–25 seconds of steady contact</span></div><div><strong>Light contact</strong><span>Cover the rear lens and adjacent light without pressing hard</span></div></div>
<p>Rest the phone and your hand on a table. Start recording, then gently cover the rear camera lens and adjacent light with your fingertip. Keep light, steady contact for 20–25 seconds.</p><p><b>AE/AF lock: ON, if supported.</b> This keeps brightness and focus fixed. Keep the flash ON throughout. We remove the first 2 seconds and last 1 second, then check for unstable sections. If settling takes longer, more footage can be left out. Upload the original camera file. Stop if you feel discomfort or the phone becomes warm.</p></div>''', unsafe_allow_html=True)
    render_protocol()
    if st.session_state.pop('capture_notice', False):
        st.info('Ready for a new take. Record a fresh 20–25 second video with the flash/video light ON throughout, then upload the original file below.')
    version = st.session_state.get('capture_version', 0)
    uploaded = st.file_uploader('Upload your original fingertip video', type=['mp4', 'mov', 'avi'],
                                key=f'capture_video_{version}',
                                on_change=upload_changed, args=(f'capture_video_{version}',),
                                help='Original rear-camera video with flash/video light ON throughout (not Auto), preferably 1080p / 60 FPS for 20–25 seconds, with gentle contact.')
    analyze = False
    if uploaded is not None:
        upload_id = uploaded.file_id
        if st.session_state.get('upload_id') != upload_id:
            st.session_state.update(upload_id=upload_id, telemetry_computed=False, telemetry_data={}, short_override=False)
            st.session_state.pop('analysis_result', None)
            st.session_state.pop('capture_error', None)
            st.session_state.pop('capture_metadata', None)
            clear_confirmation_warning()
            try:
                st.session_state['capture_metadata'] = inspect_recording(uploaded)
            except (ValueError, OSError) as error:
                st.session_state['capture_error'] = str(error)
        metadata = st.session_state.get('capture_metadata')
        error = st.session_state.get('capture_error')
        if error:
            st.error(error)
        with st.container(key='capture_confirmation'):
            confirmed = st.checkbox('This is the original fingertip video, recorded with the rear flash/video light ON throughout.',
                                    key=f'capture_confirm_flash_{version}_{upload_id}',
                                    on_change=clear_confirmation_warning,
                                    help='Use the original camera file, not a screen recording. The video light must remain ON, not Auto.')
            if st.session_state.get('capture_confirmation_attempted') and not confirmed:
                st.html('<p class="capture-confirmation-required" role="alert">Check the box above to confirm your recording before analysis.</p>')
        valid_height = render_height_input(invalidate_measurement)
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
            label = 'Proceed with reduced window' if gate == 'hold' else 'Analyze recording'
            requested = st.button(label, disabled=not valid_height or gate == 'reject', width='stretch')
            if requested and not confirmed:
                st.session_state['capture_confirmation_attempted'] = True
                st.rerun()
            analyze = requested and confirmed
            if analyze:
                st.session_state['short_override'] = gate == 'hold'
        with right:
            st.button('Retake / replace video', on_click=reset_capture, width='stretch')
        st.caption('Retake clears this upload and its results. Record again in your phone’s camera app, then choose the new file.')
    elif st.session_state.get('telemetry_computed'):
        st.button('Retake / replace video', on_click=reset_capture)
    return uploaded, analyze
