"""Optical waveform processing with explicit quality and missing-value handling."""
from time import perf_counter

import numpy as np
from scipy import signal as sp_signal
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import uniform_filter1d

try:
    from .capture_policy import (MIN_DURATION, RECOMMENDED_DURATION, MAX_DURATION,
                                 SETTLING_SECONDS, RELEASE_SECONDS, RED_MIN, RED_MAX,
                                 TARGET_FS, duration_error, motion_quality)
except ImportError:
    from capture_policy import (MIN_DURATION, RECOMMENDED_DURATION, MAX_DURATION,
                                SETTLING_SECONDS, RELEASE_SECONDS, RED_MIN, RED_MAX,
                                TARGET_FS, duration_error, motion_quality)


def _values(values, minimum=2):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < minimum or not np.isfinite(values).all():
        raise ValueError(f'Provide at least {minimum} finite one-dimensional samples.')
    return values


def _rate(fs):
    try:
        fs = float(fs)
    except (TypeError, ValueError):
        raise ValueError('Sampling rate must be finite and positive.') from None
    if not np.isfinite(fs) or fs <= 0:
        raise ValueError('Sampling rate must be finite and positive.')
    return fs


def clamp_and_validate_buffer(raw_frames, original_fps):
    """Keep at most 25 seconds, then remove 2 seconds at entry and 1 at exit."""
    values = _values(raw_frames)
    try:
        fps = float(original_fps)
    except (TypeError, ValueError):
        fps = float('nan')
    fallback = not np.isfinite(fps) or fps <= 0
    fps = 30.0 if fallback else fps
    duration = len(values) / fps
    if duration < MIN_DURATION:
        raise ValueError(duration_error(duration))
    values = values[:int(fps * MAX_DURATION)]
    processed_duration = len(values) / fps
    first = int(np.ceil(SETTLING_SECONDS * fps))
    last = len(values) - int(np.ceil(RELEASE_SECONDS * fps))
    values = _values(values[first:last])
    mean_red = float(values.mean())
    if mean_red > RED_MAX:
        raise ValueError(f'OVEREXPOSED RECORDING: Mean red intensity {mean_red:.1f} > 250. '
                         'Use light finger contact and check the camera exposure. Brightness alone cannot identify the cause.')
    if mean_red < RED_MIN:
        raise ValueError(f'INADEQUATE ILLUMINATION: Mean red intensity {mean_red:.1f} < 30. '
                         'Check that the light is enabled and the finger pad covers the lens and light.')
    if np.ptp(values) < .2:
        raise ValueError('Signal too weak: no usable brightness variation. Re-record with steady, light contact.')
    metadata = dict(recorded_duration=duration, processed_duration=processed_duration,
                    usable_duration=len(values) / fps, is_short_duration=duration < RECOMMENDED_DURATION,
                    was_clamped=duration > MAX_DURATION, fps_fallback=fallback, mean_red=mean_red,
                    settling_seconds=SETTLING_SECONDS, release_seconds=RELEASE_SECONDS)
    metadata.update(motion_quality(values, fps))
    return values, fps, metadata


def resample_signal(raw_signal, original_fps, target_fs=TARGET_FS, *, source_times=None):
    """PCHIP preserves sample shape; a denser grid adds no camera information."""
    values = _values(raw_signal)
    fps, target_fs = _rate(original_fps), _rate(target_fs)
    source = np.arange(len(values)) / fps if source_times is None else _values(source_times)
    if len(source) != len(values) or np.any(np.diff(source) <= 0):
        raise ValueError('Source timestamps must be finite, increasing and match the signal.')
    source = source - source[0]
    count = source[-1] * target_fs
    if not np.isfinite(count) or count > 200_000:
        raise ValueError('Resampling grid is too large. Check frame timestamps and sampling rates.')
    target = np.arange(0, source[-1], 1 / target_fs)
    if len(target) < 2:
        raise ValueError('The signal is too short for the requested processing rate.')
    return target, PchipInterpolator(source, values, extrapolate=False)(target)


def bandpass_filter(signal, fs=TARGET_FS, lowcut=.5, highcut=8.5, order=4):
    """Apply a Butterworth bandpass as forward/backward second-order sections."""
    values = _values(signal, 4)
    fs = _rate(fs)
    if not 0 < lowcut < highcut < fs / 2 or int(order) != order or order < 1:
        raise ValueError('Filter cutoffs must lie below Nyquist and the order must be a positive integer.')
    sos = sp_signal.butter(int(order), [lowcut, highcut], btype='bandpass', fs=fs, output='sos')
    return sp_signal.sosfiltfilt(sos, values - values.mean(), padtype='odd',
                                padlen=min(int(fs * 3), len(values) - 1))


def detrend_signal(clean_signal, fs=TARGET_FS, window_sec=.35):
    """Subtract a reflected-edge moving mean; this also changes pulse morphology."""
    values = _values(clean_signal)
    fs = _rate(fs)
    if not np.isfinite(window_sec) or window_sec <= 0:
        raise ValueError('Detrending window must be positive.')
    window = min(len(values), max(1, int(round(window_sec * fs))))
    return values - uniform_filter1d(values, size=window, mode='reflect')


def compute_smoothed_derivatives(signal, fs=TARGET_FS):
    """Return VPG and APG using a 15-sample quadratic Savitzky–Golay fit."""
    values = _values(signal, 3)
    fs = _rate(fs)
    if len(values) < 15:
        vpg = np.gradient(values, 1 / fs)
        return vpg, np.gradient(vpg, 1 / fs)
    return tuple(sp_signal.savgol_filter(values, 15, 2, deriv=d, delta=1 / fs) for d in (1, 2))


def detect_cardiac_cycles(detrended_wave, fs=TARGET_FS, max_bpm=160.0):
    """Find candidate primary peaks and a preceding local foot for each."""
    values = _values(detrended_wave, 3)
    fs, max_bpm = _rate(fs), _rate(max_bpm)
    peaks, _ = sp_signal.find_peaks(values, distance=max(1, int(fs * 60 / max_bpm)),
                                    prominence=max(.25 * values.std(), 1e-4))
    feet = []
    for i, peak in enumerate(peaks):
        period = peaks[i] - peaks[i - 1] if i else (peaks[1] - peak if len(peaks) > 1 else fs * .8)
        start = max(0, int(peak - .45 * period))
        feet.append(start + int(np.argmin(values[start:peak])) if peak > start else int(peak))
    return peaks, np.asarray(feet, dtype=int)


def _quality_beats(wave, peaks, feet):
    beats, ids = [], []
    for i in range(len(peaks) - 1):
        start, end = feet[i], feet[i + 1]
        if not 0 <= start < peaks[i] < end <= len(wave) or end - start < 8:
            continue
        beat = wave[start:end]
        span = float(np.ptp(beat))
        if span < 1e-8:
            continue
        normalized = (beat - beat.min()) / span
        beats.append(np.interp(np.linspace(0, 1, 100), np.linspace(0, 1, len(beat)), normalized))
        ids.append(i)
    if not beats:
        return set(), 0.0, []
    beats = np.asarray(beats)
    template = np.median(beats, axis=0)
    centered = beats - beats.mean(axis=1, keepdims=True)
    template = template - template.mean()
    denominator = np.linalg.norm(centered, axis=1) * np.linalg.norm(template)
    correlations = np.divide(centered @ template, denominator, out=np.zeros(len(beats)), where=denominator > 1e-12)
    return {i for i, r in zip(ids, correlations) if r >= .8}, float(np.median(correlations)), correlations.tolist()


def extract_hemodynamic_indices(clean_wave, vpg, apg, peaks, feet, fs=TARGET_FS, height_m=1.75):
    """Estimate height/delay SI and foot-referenced RI from repeatable beats.

    Shoulder candidates are reported separately. Neither a waveform shoulder nor
    a high template correlation establishes arterial stiffness or disease.
    """
    wave, vpg, apg = (_values(v, 3) for v in (clean_wave, vpg, apg))
    fs = _rate(fs)
    if not .5 <= height_m <= 2.5 or not np.isfinite(height_m):
        raise ValueError('Height must be between 0.5 and 2.5 meters.')
    peaks, feet = np.asarray(peaks, dtype=int), np.asarray(feet, dtype=int)
    if len(wave) != len(vpg) or len(wave) != len(apg) or len(peaks) != len(feet):
        raise ValueError('Waveform, derivative and landmark arrays must align.')
    if len(peaks) and (np.any(np.diff(peaks) <= 0) or np.any(peaks < 0) or np.any(peaks >= len(wave)) or np.any(feet < 0) or np.any(feet > peaks)):
        raise ValueError('Landmark indices are out of order or out of range.')
    valid, sqi, correlations = _quality_beats(wave, peaks, feet)
    records = []
    for i in sorted(valid):
        peak, next_peak = int(peaks[i]), int(peaks[i + 1])
        period = next_peak - peak
        amp_sys = float(wave[peak] - wave[feet[i]])
        if amp_sys <= 1e-8:
            continue
        lo = min(len(wave), peak + max(1, int(.10 * period)))
        hi = min(len(wave), int(feet[i + 1]), peak + int(.55 * period))
        if hi - lo < 3:
            continue
        local, props = sp_signal.find_peaks(wave[lo:hi], prominence=.01 * amp_sys)
        method = 'peak'
        if len(local):
            reflection = lo + int(local[np.argmax(props['prominences'])])
        else:
            # A negative VPG maximum marks flattening on a descending shoulder.
            local, props = sp_signal.find_peaks(vpg[lo:hi], prominence=max(1e-8, .01 * np.ptp(vpg[lo:hi])))
            local = local[(vpg[lo + local] < 0) & (wave[lo + local] > wave[feet[i]])]
            if not len(local):
                continue
            reflection = lo + int(local[np.argmax(vpg[lo + local])])
            method = 'shoulder'
        delay = (reflection - peak) / fs
        if delay < .05:
            continue
        ri = float((wave[reflection] - wave[feet[i]]) / amp_sys * 100)
        si = float(height_m / delay)
        if not np.isfinite(si + ri) or not 0 < ri < 100:
            continue
        stop = min(len(apg), peak + max(1, int(.1 * period)))
        a_start = int(feet[i])
        a_idx = a_start + int(np.argmax(apg[a_start:stop]))
        b_stop = min(hi, a_idx + max(2, int(.25 * period)))
        ba = None
        if b_stop > a_idx + 1 and apg[a_idx] > 1e-5:
            b_idx = a_idx + 1 + int(np.argmin(apg[a_idx + 1:b_stop]))
            if apg[b_idx] < 0:
                ba = float(apg[b_idx] / apg[a_idx])
        records.append(dict(beat=i, reflection=reflection, method=method, si=si, ri=ri, delay=delay, ba_ratio=ba,
                            outside_reference_bounds=not (4 <= si <= 18 and 20 <= ri <= 98)))
    enough = len(valid) >= 4 and len(records) >= 4
    def median(key):
        values = [r[key] for r in records if r[key] is not None]
        return float(np.median(values)) if enough and values else None
    return dict(si=median('si'), ri=median('ri'), ba_ratio=median('ba_ratio'), sqi_score=sqi,
                accepted_beats=len(valid), reflection_beats=len(records), beat_correlations=correlations,
                reflection_records=records, status='OK' if enough else 'LOW_QUALITY')


def assess_beat_intervals(peaks, fs=TARGET_FS):
    """Check interval consistency within the supported processing range.

    Uneven intervals can have physiological or recording causes. This heuristic
    does not distinguish them and is not an arrhythmia detector.
    """
    peaks = np.asarray(peaks)
    fs = _rate(fs)
    if peaks.ndim != 1 or not np.isfinite(peaks).all() or np.any(np.diff(peaks) <= 0):
        raise ValueError('Peak indices must be finite and strictly increasing.')
    if len(peaks) < 3:
        return dict(bpm=None, interval_cv=None, timing_quality=False,
                    timing_warnings=['Too few pulse intervals to check timing consistency.'])
    intervals = np.diff(peaks) / fs
    mean = float(np.mean(intervals))
    cv = float(np.std(intervals) / mean)
    bpm = float(60 / np.median(intervals))
    in_range = 40 <= 60 / mean <= 160 and 40 <= bpm <= 160
    consistent = in_range and cv <= .20
    warnings = [] if consistent else [
        'Pulse intervals are too uneven or outside the supported 40–160 BPM processing range. '
        'SI and RI are withheld. Re-record with your hand supported and light contact; '
        'this check cannot identify the cause of uneven intervals.']
    return dict(bpm=bpm if consistent else None, interval_cv=cv,
                timing_quality=consistent, timing_warnings=warnings)


def process_trimmed_signal(values, fps, height_m=1.75, source_times=None):
    """Process an already trimmed optical buffer; leave missing metrics unset."""
    start = perf_counter()
    time_axis, raw = resample_signal(values, fps, source_times=source_times)
    clean = bandpass_filter(raw)
    detrended = detrend_signal(clean)
    # Segment on the bandpassed contour; moving-mean subtraction can invent peaks.
    peaks, feet = detect_cardiac_cycles(clean)
    vpg, apg = compute_smoothed_derivatives(clean)
    indices = extract_hemodynamic_indices(clean, vpg, apg, peaks, feet, height_m=height_m)
    timing = assess_beat_intervals(peaks)
    if not timing['timing_quality']:
        indices.update(si=None, ri=None, ba_ratio=None, status='LOW_QUALITY')
    return dict(clean_signal=clean, detrended_signal=detrended, raw_signal=raw - raw.mean(), time_axis=time_axis,
                peaks=peaks, feet=feet, vpg=vpg, apg=apg, **timing,
                latency_ms=(perf_counter() - start) * 1000, **indices)


def compute_full_telemetry(raw_signal, original_fps, height_m=1.75):
    """Run the array API. The video API separately enforces short-clip consent."""
    start = perf_counter()
    values, fps, metadata = clamp_and_validate_buffer(raw_signal, original_fps)
    telemetry = process_trimmed_signal(values, fps, height_m)
    telemetry.update(metadata, latency_ms=(perf_counter() - start) * 1000)
    return telemetry


# Compatibility names used by scripts and earlier callers.
def detect_beats(clean_wave, fs=TARGET_FS, max_bpm=160):
    return detect_cardiac_cycles(clean_wave, fs, max_bpm)[0]


def compute_indices(clean_wave, beat_peaks, fs=TARGET_FS, **kwargs):
    wave = _values(clean_wave, 3)
    peaks = np.asarray(beat_peaks, dtype=int)
    if peaks.ndim != 1 or (len(peaks) and (np.any(peaks < 0) or np.any(peaks >= len(wave)) or np.any(np.diff(peaks) <= 0))):
        raise ValueError('Peak indices must be increasing and within the waveform.')
    if not assess_beat_intervals(peaks, fs)['timing_quality']:
        return None, None
    detected, feet = detect_cardiac_cycles(wave, fs)
    if not np.array_equal(peaks, detected):
        feet = np.array([max(0, int(p - .45 * (peaks[i] - peaks[i - 1] if i else fs * .8))) for i, p in enumerate(peaks)])
        feet = np.array([f + np.argmin(wave[f:p]) if p > f else p for f, p in zip(feet, peaks)])
    vpg, apg = compute_smoothed_derivatives(wave, fs)
    result = extract_hemodynamic_indices(wave, vpg, apg, peaks, feet, fs, kwargs.get('height_m', 1.75))
    return result['si'], result['ri']


def compute_apg_derivatives(clean_wave, fs=TARGET_FS):
    return compute_smoothed_derivatives(clean_wave, fs)


def second_derivative(clean_wave, dt):
    return compute_smoothed_derivatives(clean_wave, 1 / _rate(dt))[1]


def make_test_beat_wave(fs, duration_sec, bpm, reflection_delay_frac, reflection_amp):
    """Generate two smooth pulses per cycle for software checks, not patient data."""
    t = np.arange(int(duration_sec * fs)) / fs
    phase = (t % (60 / bpm))
    return (np.exp(-.5 * ((phase - .16) / .045) ** 2) +
            reflection_amp * np.exp(-.5 * ((phase - .16 - reflection_delay_frac * 60 / bpm) / .04) ** 2))


def self_test():
    profiles = []
    for name, delay, amplitude in [('later pulse', .22, .65), ('earlier pulse', .11, .35)]:
        raw = 170 + 45 * make_test_beat_wave(60, 20, 72, delay / (60 / 72), amplitude)
        result = compute_full_telemetry(raw, 60)
        profiles.append(result)
        print(f"{name:14s} SI={result['si']} m/s  RI={result['ri']}%  SQI={result['sqi_score']:.3f}  {result['latency_ms']:.2f} ms")
    assert all(r['status'] == 'OK' for r in profiles)
    assert profiles[1]['si'] > profiles[0]['si']
    assert profiles[1]['ri'] < profiles[0]['ri']
    _, _, meta = clamp_and_validate_buffer(np.tile([170., 180.], 1200), 60)
    assert meta['processed_duration'] == 25.0 and meta['was_clamped']
    timings = []
    for _ in range(10):
        timings.append(compute_full_telemetry(raw, 60)['latency_ms'])
    median_ms = float(np.median(timings))
    assert median_ms < 25.0, f'Local median array processing took {median_ms:.2f} ms'
    print(f'Array checks passed; warmed median {median_ms:.2f} ms. Timings are local measurements, not device guarantees.')


if __name__ == '__main__':
    self_test()
