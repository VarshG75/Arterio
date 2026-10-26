"""Reproducible local signal-only benchmark; excludes video decoding and rendering."""
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app_and_ml'))
from signal_processing.math_engine import process_trimmed_signal, make_test_beat_wave


def main():
    fs, count, runs, warmups = 60, 1000, 200, 20
    wave = make_test_beat_wave(fs, count / fs, 72, .34, .4)
    def execute():
        return process_trimmed_signal(wave, fs)
    for _ in range(warmups): execute()
    elapsed = []
    for _ in range(runs):
        start = perf_counter_ns()
        result = execute()
        elapsed.append((perf_counter_ns() - start) / 1e6)
    if result['status'] != 'OK' or any(result[key] is None for key in ('si', 'ri')):
        raise RuntimeError('Benchmark fixture must complete the SI/RI reporting path.')
    sources = ['app_and_ml/signal_processing/math_engine.py',
               'app_and_ml/signal_processing/capture_policy.py', 'scripts/benchmark_dsp.py']
    record = {'samples': count, 'source_rate_hz': fs, 'sample_rate_hz': 200,
              'output_samples': len(result['time_axis']), 'runs': runs, 'warmup_runs': warmups,
              'median_ms': round(float(np.median(elapsed)), 3),
              'p95_ms': round(float(np.percentile(elapsed, 95)), 3),
              'platform': platform.system(), 'machine': platform.machine(),
              'os_release': platform.release(), 'python': platform.python_version(),
              'numpy': np.__version__, 'scipy': scipy.__version__,
              'generated_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'fixture': {'type': 'generated two-pulse waveform, already trimmed', 'bpm': 72,
                          'reflection_delay_fraction': .34, 'reflection_amplitude': .4},
              'result': {key: result[key] for key in ('status', 'accepted_beats', 'reflection_beats', 'si', 'ri')},
              'timings_ms': [round(value, 6) for value in elapsed],
              'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
              'scope': 'PCHIP + SOS filter design/execution + detrending + segmentation + template quality + reflection ratios + smoothed derivatives; 1,000 already-trimmed generated samples at 60 Hz, resampled to 200 Hz. Excludes upload handling, video decoding, capture gates, trimming and UI.'}
    (ROOT / 'app_and_ml/assets/architecture/benchmark.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))

if __name__ == '__main__': main()
