"""Numerical regressions on generated signals with known landmarks."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app_and_ml'))
from signal_processing.capture_policy import duration_gate, motion_quality
from signal_processing.math_engine import (bandpass_filter, clamp_and_validate_buffer, compute_full_telemetry,
    compute_smoothed_derivatives, detect_cardiac_cycles, extract_hemodynamic_indices,
    make_test_beat_wave, resample_signal)


class MathEngineTests(unittest.TestCase):
    def test_duration_boundaries_and_trims(self):
        for duration, expected in [(11.9, 'reject'), (12, 'hold'), (19.99, 'hold'), (20, 'ready'), (40, 'ready')]:
            self.assertEqual(duration_gate(duration), expected)
        raw = np.tile([170., 180.], 1200)
        retained, fps, metadata = clamp_and_validate_buffer(raw, 60)
        self.assertEqual(len(retained), 22 * 60)
        self.assertEqual(metadata['processed_duration'], 25)
        self.assertEqual(metadata['recorded_duration'], 40)
        self.assertTrue(metadata['was_clamped'])
        _, fallback, metadata = clamp_and_validate_buffer(raw, np.nan)
        self.assertEqual(fallback, 30)
        self.assertTrue(metadata['fps_fallback'])
        for bad in ([1, np.nan], [[1, 2]], [1, 2]):
            with self.assertRaises(ValueError): clamp_and_validate_buffer(bad, 30)

    def test_pchip_does_not_overshoot_steps(self):
        _, values = resample_signal([0, 0, 1, 1, 0, 0], 30)
        self.assertGreaterEqual(values.min(), 0)
        self.assertLessEqual(values.max(), 1)
        with self.assertRaises(ValueError): resample_signal([1, 2, 3], 30, source_times=[0, .1, .1])

    def test_sos_stays_finite_and_rejects_stopband(self):
        t = np.arange(4000) / 200
        pulse = np.sin(2 * np.pi * 1.2 * t)
        clean = bandpass_filter(180 + pulse + 2 * np.sin(2 * np.pi * 30 * t))
        self.assertTrue(np.isfinite(clean).all())
        self.assertLess(np.std(clean[600:-600] - pulse[600:-600]), .05)
        with self.assertRaises(ValueError): bandpass_filter(pulse, highcut=110)

    def test_derivatives_and_first_foot_do_not_wrap(self):
        t = np.arange(100) / 200
        vpg, apg = compute_smoothed_derivatives(t * t)
        np.testing.assert_allclose(vpg[10:-10], 2 * t[10:-10], atol=1e-8)
        np.testing.assert_allclose(apg[10:-10], 2, atol=1e-8)
        wave = np.sin(np.arange(400) / 200 * 2 * np.pi + 1)
        peaks, feet = detect_cardiac_cycles(wave)
        self.assertTrue(np.all(feet >= 0))
        self.assertTrue(np.all(feet <= peaks))
        for bad in ([1], [1, np.inf, 3]):
            with self.assertRaises(ValueError): compute_smoothed_derivatives(bad)

    def test_known_delay_ordering_and_height_units(self):
        results = []
        for delay, amplitude in [(.22, .65), (.11, .35)]:
            raw = 170 + 45 * make_test_beat_wave(60, 20, 72, delay / (60 / 72), amplitude)
            result = compute_full_telemetry(raw, 60)
            self.assertEqual(result['status'], 'OK')
            self.assertAlmostEqual(result['bpm'], 72, delta=2)
            self.assertAlmostEqual(result['si'], 1.75 / delay, delta=1)
            expected_method = 'peak' if delay == .22 else 'shoulder'
            self.assertTrue(any(item['method'] == expected_method for item in result['reflection_records']))
            results.append(result)
        self.assertGreater(results[1]['si'], results[0]['si'])
        self.assertLess(results[1]['ri'], results[0]['ri'])
        low = compute_full_telemetry(raw, 60, height_m=1.5)
        self.assertAlmostEqual(low['si'] / results[1]['si'], 1.5 / 1.75)

    def test_missing_landmarks_stay_missing(self):
        wave = np.zeros(500)
        result = extract_hemodynamic_indices(wave, wave, wave, np.array([], int), np.array([], int))
        self.assertEqual(result['status'], 'LOW_QUALITY')
        self.assertIsNone(result['si'])
        self.assertIsNone(result['ri'])
        self.assertIsNone(result['ba_ratio'])

    def test_motion_warning_responds_to_a_local_spike(self):
        values = np.sin(np.arange(1200) / 60 * 2 * np.pi)
        self.assertFalse(motion_quality(values, 60)['motion_warning'])
        values[600] += 50
        self.assertTrue(motion_quality(values, 60)['motion_warning'])


if __name__ == '__main__': unittest.main()
