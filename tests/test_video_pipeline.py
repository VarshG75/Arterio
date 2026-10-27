"""Decoder and signal regressions using generated video, never patient data."""
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app_and_ml'))
from signal_processing.video_pipeline import analyze_live_video
from signal_processing.math_engine import resample_signal, compute_apg_derivatives, make_test_beat_wave


class VideoPipelineTests(unittest.TestCase):
    def video(self, directory, name, seconds, intensity):
        path = str(Path(directory) / (name + '.avi'))
        writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'MJPG'), 30, (32, 32))
        self.assertTrue(writer.isOpened())
        try:
            for frame in range(int(seconds * 30)):
                image = np.zeros((32, 32, 3), np.uint8)
                image[:, :, 2] = np.uint8(intensity(frame / 30))
                writer.write(image)
        finally:
            writer.release()
        return path

    def test_video_errors_are_actionable(self):
        with tempfile.TemporaryDirectory() as directory:
            cases = [('short', 2, lambda t: 180, 'CAPTURE REJECTED'),
                     ('dark', 20, lambda t: 10, 'ILLUMINATION'),
                     ('saturated', 20, lambda t: 255, 'OVEREXPOSED'),
                     ('flat', 20, lambda t: 180, 'weak')]
            for name, duration, intensity, message in cases:
                with self.subTest(name=name):
                    result = analyze_live_video(self.video(directory, name, duration, intensity))
                    self.assertEqual(result['quality'], 'error')
                    self.assertIn(message, result['message'])
                    self.assertIsNone(result['stiffness_index'])
            invalid = Path(directory) / 'invalid.mp4'
            invalid.write_bytes(b'not a video')
            self.assertEqual(analyze_live_video(str(invalid))['quality'], 'error')

    def test_optical_pulse_frequency_survives_decoding(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.video(directory, 'pulse', 20, lambda t: 180 + 20 * np.sin(2 * np.pi * 1.2 * t))
            result = analyze_live_video(path)
            self.assertIn(result['quality'], ('good', 'partial'), result['message'])
            self.assertAlmostEqual(result['heart_rate_bpm'], 72, delta=3)
            self.assertEqual(result['sample_rate_hz'], 200)
            self.assertEqual(len(result['apg_array']), len(result['clean_wave_array']))
            # A single sinusoid should not produce a confident reflection metric.
            self.assertEqual(result['quality'], 'partial')

    def test_short_video_waits_for_explicit_override(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.video(directory, 'short_pulse', 15, lambda t: 180 + 20 * np.sin(2 * np.pi * 1.2 * t))
            held = analyze_live_video(path)
            self.assertEqual(held['quality'], 'hold')
            self.assertEqual(held['clean_wave_array'], [])
            accepted = analyze_live_video(path, allow_short=True)
            self.assertIn(accepted['quality'], ('good', 'partial'))
            self.assertTrue(accepted['is_short_duration'])
            self.assertAlmostEqual(accepted['recorded_duration'], 15)

    def test_interpolation_and_derivatives_validate_input(self):
        for bad in ([1], [1, np.nan, 3]):
            with self.assertRaises(ValueError):
                resample_signal(bad, 30)
        t, wave = resample_signal(np.sin(np.arange(60) / 30), 30)
        self.assertAlmostEqual(t[1] - t[0], .005)
        vpg, apg = compute_apg_derivatives(wave)
        self.assertEqual(vpg.shape, apg.shape)
        self.assertTrue(np.isfinite(apg).all())

    def test_progress_follows_decoded_frames_and_finishes_after_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.video(directory, 'progress', 20, lambda t: 180 + 20 * np.sin(2 * np.pi * 1.2 * t))
            events = []
            result = analyze_live_video(path, progress=lambda value, message: events.append((value, message)))
            self.assertIn(result['quality'], ('good', 'partial'))
            fractions = [value for value, _ in events]
            self.assertEqual(fractions, sorted(fractions))
            self.assertEqual(fractions[-1], 1)
            self.assertTrue(any('600 / 600 expected frames' in message for _, message in events))
            self.assertIn('Checking capture quality', events[-4][1])
            self.assertIn('Analyzing waveform', events[-3][1])

    def test_rejected_capture_does_not_report_completed_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.video(directory, 'dark_progress', 20, lambda t: 10)
            events = []
            result = analyze_live_video(path, progress=lambda value, message: events.append((value, message)))
            self.assertEqual(result['quality'], 'error')
            self.assertLess(max(value for value, _ in events), 1)

    def test_late_settling_is_excluded_before_video_measurements(self):
        with tempfile.TemporaryDirectory() as directory:
            pulse = 170 + 45 * make_test_beat_wave(30, 25, 72, .22 / (60 / 72), .65)
            def intensity(time):
                if 2 <= time < 6:
                    return 180 + 45 * np.sin(2 * np.pi * 12 * time)
                return pulse[min(len(pulse) - 1, round(time * 30))]
            result = analyze_live_video(self.video(directory, 'late_settling', 25, intensity))
            self.assertEqual(result['quality'], 'good', result['message'])
            self.assertGreater(result['analysis_window'][0], 6)
            self.assertAlmostEqual(result['time_axis'][0], result['analysis_window'][0])
            self.assertLessEqual(result['time_axis'][-1], result['analysis_window'][1])
            self.assertAlmostEqual(result['stiffness_index'], 1.75 / .22, delta=1)
            self.assertGreater(len(result['capture_time_axis']), len(result['raw_wave_array']) / 200 * 30)

    def test_noise_throughout_does_not_report_a_pulse_or_indices(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.video(directory, 'all_noise', 20, lambda t: 170 + 40 * np.sin(2 * np.pi * 12 * t))
            result = analyze_live_video(path)
            self.assertEqual(result['quality'], 'error')
            self.assertIn('stable section', result['message'])
            self.assertIsNone(result['heart_rate_bpm'])
            self.assertIsNone(result['stiffness_index'])
            self.assertIsNone(result['reflection_index'])


if __name__ == '__main__':
    unittest.main()
