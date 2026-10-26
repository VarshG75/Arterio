"""Reproducible local signal-only benchmark; excludes video decoding and rendering."""
import json
import platform
import sys
from pathlib import Path
from time import perf_counter_ns

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app_and_ml'))
from signal_processing.math_engine import process_trimmed_signal, make_test_beat_wave


def main():
    fs, count, runs = 200, 1000, 200
    wave = make_test_beat_wave(fs, count / fs, 72, .34, .4)
    def execute():
        process_trimmed_signal(wave, fs)
    for _ in range(20): execute()
    elapsed = []
    for _ in range(runs):
        start = perf_counter_ns()
        execute()
        elapsed.append((perf_counter_ns() - start) / 1e6)
    record = {'samples': count, 'sample_rate_hz': fs, 'runs': runs,
              'median_ms': round(float(np.median(elapsed)), 3),
              'p95_ms': round(float(np.percentile(elapsed, 95)), 3),
              'platform': platform.system(), 'machine': platform.machine(),
              'python': platform.python_version(),
              'scope': 'PCHIP + SOS filter design/execution + detrending + segmentation + template quality + reflection ratios + smoothed derivatives; 1,000 generated samples at 200 Hz. Excludes video decoding and UI.'}
    (ROOT / 'app_and_ml/assets/architecture/benchmark.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))

if __name__ == '__main__': main()
