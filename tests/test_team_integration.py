"""Regressions for the shared sampling and interval-quality changes."""
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app_and_ml'))
from signal_processing.math_engine import assess_beat_intervals, process_trimmed_signal, compute_indices, resample_signal
from signal_processing.video_pipeline import mean_red_channel, extract_red_signal


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
        self.assertEqual(compute_indices(result['clean_signal'], result['peaks']), (None, None))

    def test_structured_pixels_do_not_bias_the_frame_mean(self):
        frame = np.full((240, 320, 3), 180, np.uint8)
        frame[::4, ::4, 2] = 255
        self.assertAlmostEqual(mean_red_channel(frame), 184.6875)

    def test_bad_decoder_timestamps_fall_back_to_the_frame_clock(self):
        class Decoder:
            index = 0
            released = False
            def isOpened(self): return True
            def read(self):
                self.index += 1
                return (True, np.full((8, 8, 3), 180, np.uint8)) if self.index <= 3 else (False, None)
            def get(self, key): return [0, 1000 / 30, 10_000_000][self.index - 1]
            def release(self): self.released = True
        decoder = Decoder()
        metadata = {'fps': 30}
        with patch('signal_processing.video_pipeline.cv2.VideoCapture', return_value=decoder):
            times, values = extract_red_signal('unused.avi', metadata)
        np.testing.assert_allclose(times, np.arange(3) / 30)
        self.assertTrue(decoder.released)
        self.assertEqual(len(values), 3)
        self.assertTrue(metadata['timestamp_fallback'])

    def test_resampling_rejects_unbounded_time_grids(self):
        for kwargs in [dict(target_fs=1e20), dict(source_times=[0, .03, 10000])]:
            with self.assertRaisesRegex(ValueError, 'grid is too large'):
                resample_signal([170, 180, 170], 30, **kwargs)

    def test_full_frame_mean_preserves_uniform_pulse_and_small_frames(self):
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
