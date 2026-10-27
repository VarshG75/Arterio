"""Check clean-pulse retention and artifact exclusion on generated recordings."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app_and_ml'))
from signal_processing.stability import select_stable_window
from signal_processing.math_engine import make_test_beat_wave, compute_full_telemetry
from views.waveform import capture_quality_figure


class StabilityTests(unittest.TestCase):
    def pulse(self, fs=60, seconds=25):
        return 170 + 45 * make_test_beat_wave(fs, seconds, 72, .22 / (60 / 72), .65)

    def test_clean_30_and_60_fps_pulses_keep_their_full_window(self):
        for fs in (30, 60):
            result = compute_full_telemetry(self.pulse(fs), fs)
            self.assertEqual(result['status'], 'OK')
            self.assertEqual(result['excluded_duration'], 0)
            self.assertAlmostEqual(result['stable_duration'], 22)
            self.assertAlmostEqual(result['bpm'], 72, delta=2)
            self.assertAlmostEqual(result['si'], 1.75 / .22, delta=1)

    def test_slow_settling_past_two_seconds_is_left_out(self):
        fs = 60
        wave = self.pulse(fs)
        wave[2 * fs:6 * fs] = 180 + 45 * np.sin(np.arange(4 * fs) / fs * 2 * np.pi * 12)
        result = compute_full_telemetry(wave, fs)
        self.assertEqual(result['status'], 'OK')
        self.assertGreater(result['analysis_window'][0], 6)
        self.assertGreater(result['excluded_duration'], 4)
        self.assertIn('high-frequency noise', result['stability_reasons'])
        self.assertAlmostEqual(result['si'], 1.75 / .22, delta=1)

    def test_sparse_clean_pulses_are_not_mistaken_for_motion(self):
        for fps in (30, 60):
            for bpm in (40, 50, 60, 72, 90, 120, 160):
                for amplitude in (2, 20, 45):
                    with self.subTest(fps=fps, bpm=bpm, amplitude=amplitude):
                        wave = 170 + amplitude * make_test_beat_wave(fps, 22, bpm, .264, .65)
                        _, details = select_stable_window(wave, fps)
                        self.assertEqual(details['excluded_duration'], 0)
                        self.assertFalse(details['motion_warning'])

    def test_spike_and_step_do_not_reach_the_selected_window(self):
        for kind in ('spike', 'step'):
            wave = self.pulse()
            if kind == 'spike':
                wave[5 * 60] = 248
            else:
                wave[5 * 60:] += 20
            result = compute_full_telemetry(wave, 60)
            self.assertEqual(result['status'], 'OK')
            self.assertGreater(result['analysis_window'][0], 6)
            self.assertAlmostEqual(result['bpm'], 72, delta=2)
            self.assertAlmostEqual(result['si'], 1.75 / .22, delta=1)

    def test_separate_clean_sections_are_never_joined(self):
        wave = self.pulse(seconds=20)
        wave[10 * 60:11 * 60] = 255
        with self.assertRaisesRegex(ValueError, 'longest stable section'):
            compute_full_telemetry(wave, 60)

    def test_all_noisy_and_repeated_jumps_are_rejected(self):
        time = np.arange(25 * 60) / 60
        wave = 170 + 30 * np.sin(2 * np.pi * 12 * time)
        with self.assertRaisesRegex(ValueError, 'stable section'):
            compute_full_telemetry(wave, 60)
        wave = self.pulse()
        wave[::120] = 255
        with self.assertRaisesRegex(ValueError, 'stable section'):
            compute_full_telemetry(wave, 60)

    def test_time_gap_breaks_a_window_instead_of_being_interpolated(self):
        wave = self.pulse(seconds=22)
        time = 2 + np.arange(len(wave)) / 60
        time[5 * 60:] += .3
        section, details = select_stable_window(wave, 60, time)
        self.assertGreater(section.start, 5 * 60)
        self.assertIn('gaps between frames', details['stability_reasons'])
        self.assertAlmostEqual(details['analysis_window'][0], time[section.start])

    def test_fractional_frame_rate_keeps_the_exact_trim_offset(self):
        fps = 59.94
        result = compute_full_telemetry(self.pulse(fps), fps)
        expected = np.ceil(2 * fps) / fps
        self.assertAlmostEqual(result['analysis_window'][0], expected)
        self.assertAlmostEqual(result['time_axis'][0], expected)

    def test_quality_plot_keeps_the_original_clock_and_selected_bounds(self):
        data = dict(capture_time_axis=[0, 1, 2, 3, 4], capture_red_values=[170, 255, 170, 180, 170],
                    excluded_intervals=[[.5, 1.5]], analysis_window=[2, 4])
        figure = capture_quality_figure(data)
        np.testing.assert_array_equal(figure.data[0].x, data['capture_time_axis'])
        self.assertEqual((figure.layout.shapes[-1].x0, figure.layout.shapes[-1].x1), (2, 4))


if __name__ == '__main__':
    unittest.main()
