"""Exercise duration consent and result badges with generated local video uploads."""
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class TelemetryWorkflowTests(unittest.TestCase):
    def fixture(self, path, seconds, *, late_settling=False):
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'MJPG'), 30, (32, 32))
        self.assertTrue(writer.isOpened())
        try:
            for i in range(seconds * 30):
                frame = np.zeros((32, 32, 3), dtype=np.uint8)
                time = i / 30
                if late_settling:
                    phase = time % (60 / 72)
                    value = 170 + 45 * (np.exp(-.5 * ((phase - .16) / .045) ** 2)
                                        + .65 * np.exp(-.5 * ((phase - .38) / .04) ** 2))
                    if 2 <= time < 6:
                        value = 180 + 45 * np.sin(2 * np.pi * 12 * time)
                else:
                    value = 180 + 20 * np.sin(2 * np.pi * 1.2 * time)
                frame[:, :, 2] = int(value)
                writer.write(frame)
        finally:
            writer.release()

    def app(self, path):
        code = f'''import io, runpy, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, {str(ROOT / 'app_and_ml')!r})
class Upload(io.BytesIO):
    name = 'generated.avi'
    file_id = {str(path)!r}
with patch('streamlit.file_uploader', return_value=Upload(Path({str(path)!r}).read_bytes())):
    runpy.run_path({str(ROOT / 'app_and_ml/app.py')!r}, run_name='__main__')
'''
        return AppTest.from_string(code).run()

    def test_short_clip_holds_then_requires_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'short.avi'
            self.fixture(path, 15)
            app = self.app(path)
            self.assertFalse(app.session_state['telemetry_computed'])
            self.assertIn('Proceed with reduced window', app.button[0].label)
            self.assertFalse(app.button[0].disabled)
            app.button[0].click().run()
            self.assertFalse(app.exception, app.exception)
            self.assertFalse(app.session_state['telemetry_computed'])
            self.assertNotIn('analysis_result', app.session_state)
            self.assertTrue(app.session_state['capture_confirmation_attempted'])
            app.checkbox[0].check().run()
            self.assertNotIn('capture_confirmation_attempted', app.session_state)
            self.assertFalse(app.session_state['telemetry_computed'])
            app.button[0].click().run()
            self.assertFalse(app.exception, app.exception)
            self.assertTrue(app.session_state['telemetry_computed'])
            self.assertTrue(app.session_state['telemetry_data']['is_short_duration'])
            self.assertTrue(any('REDUCED SAMPLE WINDOW' in item.value for item in app.markdown))

    def test_full_clip_has_cyan_badge_and_no_override(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'full.avi'
            self.fixture(path, 20)
            app = self.app(path)
            app.checkbox[0].check().run()
            app.button[0].click().run()
            self.assertFalse(app.exception, app.exception)
            self.assertFalse(app.session_state['short_override'])
            self.assertFalse(app.session_state['telemetry_data']['is_short_duration'])
            self.assertTrue(any('20S+ RECORDING ACQUIRED' in item.value for item in app.markdown))
            app.number_input[0].set_value(180.0).run()
            self.assertFalse(app.exception, app.exception)
            self.assertFalse(app.session_state['telemetry_computed'])
            self.assertEqual(app.session_state['telemetry_data'], {})
            self.assertNotIn('analysis_result', app.session_state)

    def test_feet_inches_converts_and_input_changes_clear_old_results(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'height.avi'
            self.fixture(path, 20)
            app = self.app(path)
            app.selectbox(key='capture_height_unit').select('Feet & inches').run()
            app.number_input(key='capture_height_feet').set_value(5).run()
            app.number_input(key='capture_height_inches').set_value(11.0).run()
            self.assertFalse(app.exception, app.exception)
            self.assertAlmostEqual(app.session_state['capture_height_cm'], 180.34)
            app.checkbox[0].check().run()
            app.button[0].click().run()
            self.assertAlmostEqual(app.session_state['telemetry_data']['height_m'], 1.8034)
            app.selectbox(key='capture_height_unit').select('Centimeters').run()
            self.assertAlmostEqual(app.number_input(key='capture_height_metric').value, 180.34)
            self.assertTrue(app.session_state['telemetry_computed'])
            app.selectbox(key='capture_height_unit').select('Feet & inches').run()
            app.number_input(key='capture_height_inches').set_value(10.0).run()
            self.assertFalse(app.session_state['telemetry_computed'])
            self.assertAlmostEqual(app.session_state['capture_height_cm'], 177.8)
            app.number_input(key='capture_height_feet').set_value(8).run()
            self.assertTrue(app.button[0].disabled)
            self.assertTrue(app.error)

    def test_late_settling_result_renders_timeline_and_measured_beat(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'late_settling.avi'
            self.fixture(path, 25, late_settling=True)
            app = self.app(path)
            app.checkbox[0].check().run()
            app.button[0].click().run()
            self.assertFalse(app.exception, app.exception)
            data = app.session_state['telemetry_data']
            self.assertEqual(data['quality'], 'good')
            self.assertGreater(data['analysis_window'][0], 6)
            self.assertTrue(any(item.label == 'See which part of the recording was used' for item in app.expander))
            selector = next(item for item in app.selectbox if item.label == 'Inspect a measured beat')
            selector.select_index(1).run()
            self.assertFalse(app.exception, app.exception)
            self.assertTrue(any('SI for this beat' in item.value for item in app.markdown))
            self.assertTrue(any('Using ' in item.value and 'of the recording' in item.value for item in app.caption))


if __name__ == '__main__': unittest.main()
