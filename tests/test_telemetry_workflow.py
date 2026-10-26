"""Exercise duration consent and result badges with generated local video uploads."""
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class TelemetryWorkflowTests(unittest.TestCase):
    def fixture(self, path, seconds):
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'MJPG'), 30, (32, 32))
        self.assertTrue(writer.isOpened())
        try:
            for i in range(seconds * 30):
                frame = np.zeros((32, 32, 3), dtype=np.uint8)
                frame[:, :, 2] = int(180 + 20 * np.sin(2 * np.pi * 1.2 * i / 30))
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
            self.assertTrue(app.button[0].disabled)
            app.checkbox[0].check().run()
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


if __name__ == '__main__': unittest.main()
