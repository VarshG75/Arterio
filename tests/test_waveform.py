"""The displayed landmarks and formulas must use the actual processed samples."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app_and_ml'))
from signal_processing.math_engine import make_test_beat_wave, process_trimmed_signal
from views.waveform import measured_landmarks, beat_measurements, beat_figure, overview_figure


class WaveformTests(unittest.TestCase):
    def setUp(self):
        result = process_trimmed_signal(make_test_beat_wave(60, 1000 / 60, 72, .34, .4), 60)
        self.data = dict(time_axis=result['time_axis'], clean_wave_array=result['clean_signal'],
                         raw_wave_array=result['raw_signal'], beat_indices=result['peaks'],
                         feet_indices=result['feet'], reflection_records=result['reflection_records'], height_m=1.75)

    def test_inspector_formulas_match_reported_per_beat_values(self):
        landmarks = measured_landmarks(self.data)
        self.assertGreaterEqual(len(landmarks), 4)
        for record in landmarks:
            values = beat_measurements(self.data, record)
            self.assertAlmostEqual(values['delay'], record['delay'])
            self.assertAlmostEqual(values['si'], record['si'])
            self.assertAlmostEqual(values['ri'], record['ri'])
            self.assertLess(record['foot'], record['primary'])
            self.assertLess(record['primary'], record['secondary'])
            self.assertLess(record['secondary'], record['end'])

    def test_chart_markers_and_shaded_delay_match_the_sample_indices(self):
        landmarks = measured_landmarks(self.data)
        overview = overview_figure(self.data)
        np.testing.assert_allclose(overview.data[-1].x,
                                   np.asarray(self.data['time_axis'])[[r['secondary'] for r in landmarks]])
        record = landmarks[0]
        figure = beat_figure(self.data, record)
        self.assertEqual(figure.data[1].y[0], 0)
        delay_shape = next(shape for shape in figure.layout.shapes if shape.type == 'rect')
        self.assertAlmostEqual(delay_shape.x1 - delay_shape.x0, record['delay'] * 1000)
        self.assertAlmostEqual(figure.data[3].y[0] / figure.data[2].y[0] * 100, record['ri'])

    def test_missing_candidates_do_not_gain_invented_markers(self):
        self.data['reflection_records'] = []
        self.assertEqual(measured_landmarks(self.data), [])
        self.assertEqual(len(overview_figure(self.data).data), 3)


if __name__ == '__main__':
    unittest.main()
