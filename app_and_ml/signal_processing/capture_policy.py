"""Shared capture limits and recording-quality checks."""
import numpy as np

MIN_DURATION = 12.0
RECOMMENDED_DURATION = 20.0
MAX_DURATION = 25.0
SETTLING_SECONDS = 2.0
RELEASE_SECONDS = 1.0
TARGET_FS = 200.0
RED_MIN = 30.0
RED_MAX = 250.0


def duration_gate(duration):
    """Return reject, hold or ready without decoding the recording."""
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError('Recording duration is unavailable. Export an original 30 or 60 FPS video.')
    if duration < MIN_DURATION:
        return 'reject'
    return 'hold' if duration < RECOMMENDED_DURATION else 'ready'


def duration_error(duration):
    return (f'CAPTURE REJECTED: Video is only {duration:.1f}s. A minimum of 12.0s is required; '
            'record 20–25 seconds to leave more complete beats after trimming.')


def motion_quality(values, fps):
    """Compare half-second frame-difference variance with its median.

    This detects abrupt changes; it is not a calibrated SNR or motion classifier.
    """
    differences = np.diff(values)
    width = max(3, int(round(fps * .5)))
    variances = np.array([np.var(differences[i:i + width])
                          for i in range(0, len(differences) - width + 1, max(1, width // 2))])
    if not len(variances):
        return {'motion_warning': False, 'motion_variance_ratio': 0.0}
    baseline = max(float(np.median(variances)), 1e-6)
    ratio = float(variances.max() / baseline)
    return {'motion_warning': ratio > 4.0, 'motion_variance_ratio': ratio}
