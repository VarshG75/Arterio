"""Decode a bounded local recording and pass its optical trace to the math engine."""
import cv2
import numpy as np

from .capture_policy import (TARGET_FS, MAX_DURATION, SETTLING_SECONDS, RELEASE_SECONDS,
                             duration_gate, duration_error)
from .math_engine import clamp_and_validate_buffer, process_trimmed_signal, resample_signal


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


def extract_red_signal(filepath, metadata=None):
    """Decode at most 25 seconds; release the decoder even when a frame fails."""
    metadata = metadata or video_metadata(filepath)
    fps = metadata['fps']
    cap = cv2.VideoCapture(str(filepath))
    try:
        if not cap.isOpened():
            raise ValueError('Could not open the video.')
        times, reds = [], []
        for _ in range(int(MAX_DURATION * fps)):
            ok, frame = cap.read()
            if not ok:
                break
            times.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
            reds.append(mean_red_channel(frame))
        times, reds = np.asarray(times), np.asarray(reds)
        if len(reds) < 2:
            raise ValueError('No usable video frames. Try an original H.264 MP4.')
        gaps = np.diff(times)
        if (not np.isfinite(times).all() or np.any(gaps <= 0)
                or np.any(gaps > max(.5, 5 / fps))
                or times[-1] - times[0] > MAX_DURATION + 1):
            times = np.arange(len(reds)) / fps
        return times - times[0], reds
    finally:
        cap.release()


def resample_uniform(times, values, target_fs=TARGET_FS):
    return resample_signal(values, TARGET_FS, target_fs, source_times=times)[1]


def analyze_live_video(filepath, *, allow_short=False, height_m=1.75):
    """Short clips require explicit consent. Errors never receive invented metrics."""
    result = dict(heart_rate_bpm=None, stiffness_index=None, reflection_index=None,
                  clean_wave_array=[], raw_wave_array=[], beat_indices=[], feet_indices=[],
                  sample_rate_hz=TARGET_FS, quality='error', message='', warnings=[])
    try:
        metadata = video_metadata(filepath)
        duration = metadata['duration']
        result.update(recorded_duration=duration, is_short_duration=duration < 20, capture_metadata=metadata)
        gate = duration_gate(duration)
        if gate == 'reject':
            raise ValueError(duration_error(duration))
        if gate == 'hold' and not allow_short:
            result.update(quality='hold', message='Record 20–25 seconds, or explicitly proceed with this shorter window.')
            return result
        times, reds = extract_red_signal(filepath, metadata)
        decoded_duration = len(reds) / metadata['fps']
        actual_duration = min(duration, decoded_duration) if decoded_duration < MAX_DURATION else duration
        if duration_gate(actual_duration) == 'reject':
            raise ValueError(duration_error(actual_duration))
        if actual_duration < 20 and not allow_short:
            result.update(quality='hold', recorded_duration=actual_duration, is_short_duration=True,
                          message='Decoded footage is shorter than its metadata. Please confirm the reduced window or replace the clip.')
            return result
        values, fps, quality = clamp_and_validate_buffer(reds, metadata['fps'])
        first = int(np.ceil(SETTLING_SECONDS * fps))
        last = len(reds) - int(np.ceil(RELEASE_SECONDS * fps))
        processed = process_trimmed_signal(values, fps, height_m, times[first:last])
        quality.update(recorded_duration=actual_duration, is_short_duration=actual_duration < 20,
                       was_clamped=duration > MAX_DURATION, fps_fallback=metadata['fps_fallback'])
        warnings = list(processed['timing_warnings'])
        if quality['motion_warning']:
            warnings.append('SIGNIFICANT MOTION ARTIFACT IDENTIFIED. Keep your hand still on a flat desk. Abrupt signal changes can also come from exposure adjustments.')
        if quality['was_clamped']:
            warnings.append('Only the first 25 seconds were decoded; the 2-second start and 1-second end trims apply to that segment.')
        if quality['fps_fallback']:
            warnings.append('Frame rate was missing. A 30 FPS fallback was used; timing estimates may be inaccurate. Re-export at a known frame rate.')
        if processed['accepted_beats'] < 10:
            warnings.append('Fewer than 10 repeatable beat segments remained. Record another steady 20–25 second clip for a longer sample.')
        result.update(quality, heart_rate_bpm=processed['bpm'], stiffness_index=processed['si'],
                      reflection_index=processed['ri'], ba_ratio=processed['ba_ratio'], sqi_score=processed['sqi_score'],
                      clean_wave_array=processed['clean_signal'].tolist(), raw_wave_array=processed['raw_signal'].tolist(),
                      time_axis=processed['time_axis'].tolist(), beat_indices=processed['peaks'].tolist(),
                      feet_indices=processed['feet'].tolist(), vpg_array=processed['vpg'].tolist(), apg_array=processed['apg'].tolist(),
                      detrended_array=processed['detrended_signal'].tolist(), accepted_beats=processed['accepted_beats'],
                      reflection_beats=processed['reflection_beats'], reflection_records=processed['reflection_records'],
                      latency_ms=processed['latency_ms'], height_m=height_m, status=processed['status'], warnings=warnings,
                      interval_cv=processed['interval_cv'], timing_quality=processed['timing_quality'],
                      quality='good' if processed['status'] == 'OK' else 'partial',
                      message=('Waveform processing complete.' if processed['status'] == 'OK' else
                               'Timing quality did not pass. Pulse and reflection metrics are withheld.' if not processed['timing_quality'] else
                               'A repeatable secondary landmark could not be measured in at least four beats. Missing metrics are left blank.'))
    except (ValueError, cv2.error, OSError) as error:
        result['message'] = str(error)
    return result
