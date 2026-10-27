"""Choose one uninterrupted section before filtering; never join separated beats."""
import numpy as np

try:
    from .capture_policy import RED_MIN, RED_MAX
except ImportError:
    from capture_policy import RED_MIN, RED_MAX

MIN_STABLE_SECONDS = 8.0
GUARD_SECONDS = 1.0


def _runs(mask):
    edges = np.diff(np.r_[False, mask, False].astype(int))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def select_stable_window(values, fps, source_times=None):
    """Flag clipping, jumps and noise, then keep the longest unflagged run.

    These are recording checks, not a motion sensor or a clinical quality score.
    Thresholds are listed in docs/SIGNAL_QUALITY.md and tested on generated traces.
    """
    values = np.asarray(values, dtype=float)
    fps = float(fps)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise ValueError('The recording needs finite brightness samples.')
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError('The frame rate must be positive.')
    times = np.arange(len(values)) / fps if source_times is None else np.asarray(source_times, dtype=float)
    if (times.shape != values.shape or not np.isfinite(times).all()
            or np.any(np.diff(times) <= 0)):
        raise ValueError('Recording timestamps must increase and match the frames.')
    if np.all(values > RED_MAX):
        raise ValueError('OVEREXPOSED RECORDING: All retained frames are too bright. Use light contact and lower the exposure.')
    if np.all(values < RED_MIN):
        raise ValueError('INADEQUATE ILLUMINATION: Turn the rear video light ON and cover the lens and light.')
    if np.ptp(values) < .2:
        raise ValueError('Signal too weak: no usable brightness variation. Record again with steady, light contact.')

    bad = (values < RED_MIN) | (values > RED_MAX)
    reasons = set()
    if bad.any():
        reasons.add('brightness outside 30–250')
    differences = np.diff(values)
    center = np.median(differences)
    spread = 1.4826 * np.median(np.abs(differences - center))
    span = float(np.percentile(values, 99) - np.percentile(values, 1))
    deviations = np.abs(differences - center)
    neighbors = np.maximum(np.r_[0, deviations[:-1]], np.r_[deviations[1:], 0])
    isolated = (deviations > max(2.0, 4 * spread, .25 * span)) & (deviations > 2 * np.maximum(neighbors, 1))
    isolated[[0, -1]] = False
    jumps = np.flatnonzero((deviations > max(2.0, 8 * spread, .8 * span)) | isolated)
    if len(jumps):
        bad[jumps] = True
        bad[jumps + 1] = True
        reasons.add('abrupt brightness changes')

    width = max(3, int(round(fps * .5)))
    starts = list(range(0, len(differences) - width + 1, max(1, width // 2)))
    variances = np.array([np.var(differences[i:i + width]) for i in starts])
    reference_width = max(width, int(round(2 * fps)))
    reference_variances = [np.var(differences[i:i + reference_width])
                           for i in range(0, len(differences) - reference_width + 1, max(1, width))]
    baseline = max(float(np.median(reference_variances)), .04) if reference_variances else .04
    for i, variance in zip(starts, variances):
        if variance > 4 * baseline:
            bad[i:i + width + 1] = True
            reasons.add('uneven frame-to-frame changes')

    width = max(8, int(round(2 * fps)))
    frequencies = np.fft.rfftfreq(width, 1 / fps)
    pulse_band = (frequencies >= .5) & (frequencies <= 8.5)
    noise_band = frequencies > 8.5
    for i in range(0, len(values) - width + 1, max(1, int(round(.5 * fps)))):
        section = values[i:i + width]
        if np.percentile(section, 95) - np.percentile(section, 5) < .2:
            bad[i:i + width] = True
            reasons.add('little brightness variation')
            continue
        spectrum = np.abs(np.fft.rfft((section - section.mean()) * np.hanning(width))) ** 2
        pulse_power, noise_power = float(spectrum[pulse_band].sum()), float(spectrum[noise_band].sum())
        if noise_power > max(pulse_power, 1e-8):
            bad[i:i + width] = True
            reasons.add('high-frequency noise')

    gaps = np.flatnonzero(np.diff(times) > max(.15, 2.5 / fps))
    if len(gaps):
        bad[gaps] = True
        bad[gaps + 1] = True
        reasons.add('gaps between frames')
    flagged = bad.copy()
    for start, end in _runs(flagged):
        left = np.searchsorted(times, times[start] - GUARD_SECONDS)
        right = np.searchsorted(times, times[end - 1] + GUARD_SECONDS, side='right')
        bad[left:right] = True
    candidates = _runs(~bad)
    if not candidates:
        raise ValueError('No stable section found. Keep the phone and hand supported, use light contact and record again with the video light ON.')
    first, last = max(candidates, key=lambda run: times[run[1] - 1] - times[run[0]])
    duration = float(times[last - 1] - times[first] + 1 / fps)
    if duration + 1e-6 < MIN_STABLE_SECONDS:
        raise ValueError(f'The longest stable section is {duration:.1f}s. At least {MIN_STABLE_SECONDS:.0f}s in one continuous section is required; record another steady 20–25 second clip.')
    intervals = lambda mask: [[float(times[a]), float(times[b - 1] + 1 / fps)] for a, b in _runs(mask)]
    details = dict(analysis_window=[float(times[first]), float(times[last - 1] + 1 / fps)],
                   stable_duration=duration, excluded_duration=float((len(values) - last + first) / fps),
                   excluded_intervals=intervals(bad), stability_reasons=sorted(reasons),
                   stable_candidates=len(candidates), stability_guard_seconds=GUARD_SECONDS,
                   motion_warning=bool(bad.any()),
                   motion_variance_ratio=float(variances.max() / baseline) if len(variances) else 0.0)
    return slice(first, last), details
