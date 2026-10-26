"""Regressions for the shared sampling and interval-quality changes."""
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app_and_ml'))
from signal_processing.math_engine import assess_beat_intervals, process_trimmed_signal
from signal_processing.video_pipeline import mean_red_channel


class TeamIntegrationTests(unittest.TestCase):
    def test_interval_consistency_and_supported_range(self):
        stable = assess_beat_intervals(np.arange(20) * 160)
        self.assertTrue(stable['timing_quality'])
        self.assertAlmostEqual(stable['bpm'], 75)
        for peaks in ([0, 160], np.arange(10) * 400, np.cumsum([0, 160, 80, 240, 80, 240])):
            result = assess_beat_intervals(peaks)
            self.assertFalse(result['timing_quality'])
            self.assertIsNone(result['bpm'])
            self.assertTrue(result['timing_warnings'])

    def test_irregular_wave_does_not_report_reflection_metrics(self):
        t = np.arange(4000) / 200
        wave = np.zeros_like(t)
        for center in [1, 1.5, 2.5, 3, 4, 4.5, 5.5, 6, 7, 7.5, 8.5, 9, 10, 10.5, 11.5, 12, 13, 13.5, 14.5, 15, 16]:
            wave += np.exp(-.5 * ((t - center) / .045) ** 2)
            wave += .5 * np.exp(-.5 * ((t - center - .2) / .04) ** 2)
        result = process_trimmed_signal(170 + wave, 200)
        self.assertFalse(result['timing_quality'])
        self.assertIsNone(result['si'])
        self.assertIsNone(result['ri'])

    def test_spatial_sampling_preserves_uniform_pulse_and_small_frames(self):
        frame = np.zeros((240, 320, 3), np.uint8)
        for red in [100, 160, 200, 250]:
            frame[:, :, 2] = red
            self.assertEqual(mean_red_channel(frame), red)
        rng = np.random.default_rng(4)
        small = rng.integers(0, 256, (32, 32, 3), dtype=np.uint8)
        self.assertEqual(mean_red_channel(small), small[:, :, 2].mean())
        large = rng.integers(0, 256, (1080, 1920, 3), dtype=np.uint8)
        self.assertAlmostEqual(mean_red_channel(large), large[:, :, 2].mean(), delta=.6)


if __name__ == '__main__': unittest.main()
