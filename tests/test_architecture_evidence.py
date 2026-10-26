"""Keep the published benchmark tied to its measured implementation."""
import hashlib
import json
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class ArchitectureEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'app_and_ml/assets/architecture/benchmark.json').read_text())

    def test_benchmark_sources_match_the_recorded_revision(self):
        self.assertEqual(set(self.record['source_sha256']), {
            'app_and_ml/signal_processing/math_engine.py',
            'app_and_ml/signal_processing/capture_policy.py', 'scripts/benchmark_dsp.py'})
        for name, digest in self.record['source_sha256'].items():
            with self.subTest(source=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest,
                                 'Processing code changed; rerun scripts/benchmark_dsp.py.')

    def test_reported_statistics_and_completed_reporting_path(self):
        record = self.record
        timings = np.asarray(record['timings_ms'])
        self.assertEqual(len(timings), record['runs'])
        self.assertTrue(np.isfinite(timings).all() and np.all(timings > 0))
        self.assertAlmostEqual(record['median_ms'], np.median(timings), delta=.00051)
        self.assertAlmostEqual(record['p95_ms'], np.percentile(timings, 95), delta=.00051)
        self.assertEqual(record['result']['status'], 'OK')
        self.assertGreaterEqual(record['result']['reflection_beats'], 4)
        self.assertGreaterEqual(record['result']['accepted_beats'], 4)
        self.assertTrue(np.isfinite([record['result']['si'], record['result']['ri']]).all())
        self.assertGreater(record['output_samples'], record['samples'])
        self.assertEqual(record['source_rate_hz'], 60)
        self.assertEqual(record['sample_rate_hz'], 200)
        self.assertGreater(record['warmup_runs'], 0)


if __name__ == '__main__':
    unittest.main()
