"""Decode a bounded local recording and pass its optical trace to the math engine."""
import cv2
import numpy as np

from .capture_policy import (TARGET_FS, MAX_DURATION, SETTLING_SECONDS, RELEASE_SECONDS,
                             duration_gate, duration_error)
from .math_engine import clamp_and_validate_buffer, process_trimmed_signal, resample_signal
from .stability import select_stable_window


def video_metadata(filepath):
    cap = cv2.VideoCapture(str(filepath))
    try:
        if not cap.isOpened():
            raise ValueError('Could not open the video. Try an original H.264 MP4 or MOV file.')
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        fallback = not np.isfinite(fps) or fps <= 0
        fps = 30.0 if fallback else fps
        count = float(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if not np.isfinite(count) or count < 1 or fps > 240:
            raise ValueError('Video timing metadata is invalid. Export an original 30 or 60 FPS recording.')
        return dict(fps=fps, fps_fallback=fallback, frames=int(count), duration=count / fps,
                    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    finally:
        cap.release()


def mean_red_channel(frame):
    """Use OpenCV’s full-frame reduction without regular-grid sampling bias."""
    return float(cv2.sumElems(frame)[2] / (frame.shape[0] * frame.shape[1]))


def extract_red_signal(filepath, metadata=None, *, progress=None):
    """Decode at most 25 seconds; release the decoder even when a frame fails."""
    metadata = metadata or video_metadata(filepath)
    fps = metadata['fps']
    cap = cv2.VideoCapture(str(filepath))
    try:
        if not cap.isOpened():
            raise ValueError('Could not open the video.')
        times, reds = [], []
        limit = int(MAX_DURATION * fps)
        expected = max(1, min(limit, int(metadata.get('frames', limit))))
        update_every = max(1, expected // 40)
        for index in range(limit):
            ok, frame = cap.read()
            if not ok:
                break
            times.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
            reds.append(mean_red_channel(frame))
            if progress and (index == 0 or (index + 1) % update_every == 0):
                progress(.10 + .68 * min((index + 1) / expected, 1),
                         f'Reading video · {index + 1:,} / {expected:,} expected frames')
        times, reds = np.asarray(times), np.asarray(reds)
        if len(reds) < 2:
            raise ValueError('No usable video frames. Try an original H.264 MP4.')
        gaps = np.diff(times)
        metadata['timestamp_fallback'] = bool(not np.isfinite(times).all() or np.any(gaps <= 0)
                                              or np.any(gaps > max(.5, 5 / fps))
                                              or times[-1] - times[0] > MAX_DURATION + 1)
        if metadata['timestamp_fallback']:
            times = np.arange(len(reds)) / fps
        return times - times[0], reds
    finally:
        cap.release()


def resample_uniform(times, values, target_fs=TARGET_FS):
    return resample_signal(values, TARGET_FS, target_fs, source_times=times)[1]


REQUIRED_BEATS = 4  # Keep this in step with the math engine's reporting minimum.


def build_feedback(processed, quality):
    """Explain the quality checks and why any measurements are missing."""
    notices, missing = [], {}

    def add(level, title, body, next_step=''):
        notices.append(dict(level=level, title=title, body=body, next_step=next_step))

    accepted, landmarks, cv = processed['accepted_beats'], processed['reflection_beats'], processed['interval_cv']
    if not processed['timing_quality']:
        if cv is None:
            detail = 'Too few pulse peaks were found to check their timing.'
        elif cv > .20:
            detail = f'Beat-to-beat spacing varied by {cv:.1%} (the limit is 20%).'
        else:
            detail = 'The detected pulse rate fell outside the supported 40–160 BPM range.'
        add('error', 'Pulse timing inconsistent',
            f'{detail} Pulse rate, SI and RI are withheld because the timing check failed.',
            'Possible causes: movement, changing fingertip pressure or camera exposure changes. Support your arm, keep light, '
            'steady contact and record again. This check is not designed to detect heart-rhythm problems.')
        reason = 'Pulse timing did not pass the consistency check.'
        missing = dict(pulse=reason, si=reason, ri=reason)
    elif accepted < REQUIRED_BEATS:
        add('error', 'Insufficient consistent pulse cycles',
            f'{accepted} repeatable pulse cycles were found; {REQUIRED_BEATS} are needed. '
            'Pulse rate is still shown; SI and RI are unavailable.',
            'Possible causes: movement or uneven contact changed the pulse shape from beat to beat. '
            'Keep your fingertip still with light, steady pressure.')
        reason = f'Only {accepted} repeatable pulse cycles were found ({REQUIRED_BEATS} needed).'
        missing = dict(si=reason, ri=reason)
    elif processed['status'] != 'OK':
        add('error', 'Secondary waveform feature unavailable',
            'Too few repeatable secondary waveform landmarks were found '
            f'(measured in {landmarks} of {accepted} accepted cycles; {REQUIRED_BEATS} needed). '
            'SI and RI are withheld. Pulse rate is still shown.',
            'Possible causes: pressing too firmly can flatten the pulse shape, and some waveforms naturally show a weak '
            'secondary feature. Try lighter contact and a warm hand. A missing landmark is not a sign of disease.')
        reason = f'A secondary landmark was measured in only {landmarks} cycles ({REQUIRED_BEATS} needed).'
        missing = dict(si=reason, ri=reason)
    if quality.get('motion_warning'):
        add('info', 'Unstable sections left out',
            'Some recording sections failed brightness or stability checks. Analysis uses only the longest section that passed the '
            'stability checks; the recording timeline shows the selected interval.',
            'Support your arm, use light contact and keep AE/AF lock ON if supported.')
    if quality.get('excluded_duration', 0) > 0:
        add('info', 'Selected recording section',
            f"{quality['stable_duration']:.1f}s was kept for analysis. Other sections were left out; separate sections are never joined.")
    if processed['status'] == 'OK' and accepted < 10:
        add('info', 'Short sample',
            f'{accepted} repeatable pulse cycles were used. A longer stable section would provide more cycles.',
            'A steady 20–25 second recording usually gives more cycles.')
    if quality.get('was_clamped'):
        add('info', 'Long recording',
            'Only the first 25 seconds were decoded. Initial and final trims and stability checks apply within that segment.')
    if quality.get('fps_fallback'):
        add('warning', 'Frame rate missing',
            'The video did not report its frame rate, so 30 FPS was assumed. Timing-based values may be inaccurate.',
            'Upload the original camera file rather than an edited or exported copy.')
    if quality.get('timestamp_fallback'):
        add('warning', 'Video timestamps replaced',
            'The decoder returned unusable timestamps, so timing uses frame count and the reported FPS. '
            'Variable frame timing cannot be recovered from that clock.',
            'Use the original camera file and check the recording settings.')
    return notices, missing


def analyze_live_video(filepath, *, allow_short=False, height_m=1.75, progress=None):
    """Short clips require explicit consent. Errors never receive invented metrics."""
    result = dict(heart_rate_bpm=None, stiffness_index=None, reflection_index=None,
                  clean_wave_array=[], raw_wave_array=[], beat_indices=[], feet_indices=[],
                  sample_rate_hz=TARGET_FS, quality='error', message='', warnings=[])
    try:
        if progress:
            progress(.02, 'Checking recording metadata')
        metadata = video_metadata(filepath)
        duration = metadata['duration']
        result.update(recorded_duration=duration, is_short_duration=duration < 20, capture_metadata=metadata)
        gate = duration_gate(duration)
        if gate == 'reject':
            raise ValueError(duration_error(duration))
        if gate == 'hold' and not allow_short:
            result.update(quality='hold', message='Record 20–25 seconds, or explicitly proceed with this shorter window.')
            return result
        if progress:
            progress(.10, 'Reading video · decoding the original frames')
        times, reds = extract_red_signal(filepath, metadata, progress=progress)
        if progress:
            progress(.80, f'Checking capture quality · {len(reds):,} frames decoded')
        decoded_duration = len(reds) / metadata['fps']
        actual_duration = min(duration, decoded_duration) if decoded_duration < MAX_DURATION else duration
        if duration_gate(actual_duration) == 'reject':
            raise ValueError(duration_error(actual_duration))
        if actual_duration < 20 and not allow_short:
            result.update(quality='hold', recorded_duration=actual_duration, is_short_duration=True,
                          message='Decoded footage is shorter than its metadata. Please confirm the reduced window or replace the clip.')
            return result
        values, fps, quality = clamp_and_validate_buffer(reds, metadata['fps'], check_quality=False)
        first = int(np.ceil(SETTLING_SECONDS * fps))
        last = len(reds) - int(np.ceil(RELEASE_SECONDS * fps))
        retained_times = times[first:last]
        section, stability = select_stable_window(values, fps, retained_times)
        quality.update(stability, mean_red=float(values[section].mean()))
        if progress:
            progress(.88, 'Analyzing waveform · filtering and locating pulse landmarks')
        processed = process_trimmed_signal(values[section], fps, height_m, retained_times[section])
        if progress:
            progress(.96, 'Preparing waveform and measurement results')
        quality.update(recorded_duration=actual_duration, is_short_duration=actual_duration < 20,
                       was_clamped=duration > MAX_DURATION, fps_fallback=metadata['fps_fallback'],
                       timestamp_fallback=metadata.get('timestamp_fallback', False))
        offset = float(retained_times[section.start])
        notices, missing = build_feedback(processed, quality)
        warnings = [f"{n['title'].upper()}: {n['body']}" for n in notices]
        errors = [n['body'] for n in notices if n['level'] == 'error']
        result.update(quality, heart_rate_bpm=processed['bpm'], stiffness_index=processed['si'],
                      reflection_index=processed['ri'], ba_ratio=processed['ba_ratio'], sqi_score=processed['sqi_score'],
                      clean_wave_array=processed['clean_signal'].tolist(), raw_wave_array=processed['raw_signal'].tolist(),
                      capture_time_axis=times.tolist(), capture_red_values=reds.tolist(),
                      time_axis=(processed['time_axis'] + offset).tolist(), time_offset_s=offset,
                      beat_indices=processed['peaks'].tolist(),
                      feet_indices=processed['feet'].tolist(), vpg_array=processed['vpg'].tolist(), apg_array=processed['apg'].tolist(),
                      detrended_array=processed['detrended_signal'].tolist(), accepted_beats=processed['accepted_beats'],
                      reflection_beats=processed['reflection_beats'], reflection_records=processed['reflection_records'],
                      latency_ms=processed['latency_ms'], height_m=height_m, status=processed['status'], warnings=warnings,
                      notices=notices, missing_reasons=missing,
                      interval_cv=processed['interval_cv'], timing_quality=processed['timing_quality'],
                      quality='good' if processed['status'] == 'OK' else 'partial',
                      message='Waveform processing complete.' if processed['status'] == 'OK' else errors[0])
        if progress:
            progress(1.0, 'Waveform ready')
    except (ValueError, cv2.error, OSError) as error:
        result['message'] = str(error)
    return result
