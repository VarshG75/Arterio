"""
video_pipeline.py — Part 2: Hardware Bridge (Shreyas / Person A)

video file -> red-channel signal -> uniform sample rate -> math_engine -> dict
"""

import cv2
import numpy as np
from scipy.interpolate import CubicSpline

try:  # works whether imported from app.py's package path or run from this folder
    from signal_processing.math_engine import bandpass_filter, detect_beats, compute_indices
except ImportError:
    from math_engine import bandpass_filter, detect_beats, compute_indices

TARGET_FS = 100.0  # every video gets resampled to 100 samples/second


def extract_red_signal(filepath: str):
    """
    Step 1: open the video and, for every frame, average the red channel.
    Returns (times_sec, red_values). Uses each frame's real timestamp,
    because phones don't always record at an exact, steady frame rate.
    """
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise ValueError("Could not open the video. Try an .mp4 (H.264) file.")

    nominal_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    times, reds = [], []
    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        # OpenCV frames are B, G, R order -> red is channel index 2
        reds.append(float(frame[::4, ::4, 2].mean()))
        times.append(t_ms / 1000.0 if t_ms and t_ms > 0 else frame_index / nominal_fps)
        frame_index += 1
    cap.release()

    times = np.asarray(times)
    reds = np.asarray(reds)
    # timestamps must strictly increase for the spline; fall back to a steady clock if not
    if len(times) < 2 or np.any(np.diff(times) <= 0):
        times = np.arange(len(reds)) / nominal_fps
    return times, reds


def resample_uniform(times: np.ndarray, values: np.ndarray, target_fs: float = TARGET_FS):
    """
    Step 2: fit a smooth cubic-spline curve through the samples, then read it
    off at perfectly even spacing (target_fs times per second).
    """
    t_new = np.arange(times[0], times[-1], 1.0 / target_fs)
    return CubicSpline(times, values)(t_new)


def analyze_live_video(filepath: str) -> dict:
    """The one function Varsh's app calls. Returns a dict (see keys below)."""
    empty = {"heart_rate_bpm": None, "stiffness_index": None,
             "reflection_index": None, "clean_wave_array": [],
             "raw_wave_array": [], "beat_indices": [],
             "sample_rate_hz": TARGET_FS, "quality": "error", "message": ""}
    try:
        times, reds = extract_red_signal(filepath)
    except ValueError as e:
        empty["message"] = str(e)
        return empty

    duration = times[-1] - times[0] if len(times) > 1 else 0
    if duration < 5:
        empty["message"] = "Video too short — record at least 10 seconds."
        return empty

    # Quality check: no finger on the lens / no flash => red channel too dark
    # or barely changing at all.
    if reds.mean() < 100 or np.ptp(reds) < 0.2:
        empty["quality"] = "bad"
        empty["message"] = "Signal too weak — cover the camera AND flash fully with your fingertip."
        return empty

    raw = resample_uniform(times, reds)
    clean = bandpass_filter(raw, fs=TARGET_FS)
    if len(clean) > 5 * TARGET_FS:  # drop first 2s (exposure settling) and last 1s (filter edge)
        raw, clean = raw[int(2 * TARGET_FS):-int(TARGET_FS)], clean[int(2 * TARGET_FS):-int(TARGET_FS)]
    raw = raw - raw.mean()  # center for plotting
    beats = detect_beats(clean, fs=TARGET_FS)

    if len(beats) < 3:
        empty["quality"] = "bad"
        empty["message"] = "Couldn't find enough heartbeats — hold still and retry."
        return empty

    intervals = np.diff(beats) / TARGET_FS
    bpm = float(60.0 / np.mean(intervals))
    spread = float(np.std(intervals) / np.mean(intervals))
    if not (40 <= bpm <= 180) or spread > 0.20:
        empty["quality"] = "poor"
        empty["message"] = ("The pulse signal was too irregular to measure reliably. "
                            "Cover the camera and flash fully, rest your hand on a table, "
                            "press lightly, and stay still for 20 seconds.")
        return empty
    si, ri = compute_indices(clean, beats, fs=TARGET_FS)
    return {"heart_rate_bpm": round(bpm, 1),
            "stiffness_index": None if si is None else round(si, 3),
            "reflection_index": None if ri is None else round(ri, 3),
            "clean_wave_array": clean.tolist(),
            "raw_wave_array": raw.tolist(),
            "beat_indices": beats.tolist(),
            "sample_rate_hz": TARGET_FS,
            "quality": "good" if si is not None else "partial",
            "message": f"{len(beats)} beats analyzed over {duration:.0f}s"}
