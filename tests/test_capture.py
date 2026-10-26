"""Retaking a recording must invalidate its upload and stored measurements."""
import sys
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]

class CaptureTests(unittest.TestCase):
    def test_retake_resets_results_and_replaces_uploader(self):
        code=f"import sys\nsys.path.insert(0, {str(ROOT / 'app_and_ml')!r})\nfrom views.capture import render_capture\nrender_capture()"
        app=AppTest.from_string(code)
        app.session_state['telemetry_computed']=True
        app.session_state['telemetry_data']={'bpm':72}
        app.session_state['capture_metadata']={'fps':60}
        app.session_state['upload_id']='old-file'
        app.run()
        self.assertEqual(len(app.exception),0)
        app.button[0].click().run()
        self.assertEqual(len(app.exception),0)
        self.assertFalse(app.session_state['telemetry_computed'])
        self.assertEqual(app.session_state['telemetry_data'],{})
        self.assertEqual(app.session_state['capture_version'],1)
        self.assertNotIn('capture_metadata',app.session_state)
        self.assertNotIn('upload_id',app.session_state)
        self.assertEqual(app.get('file_uploader')[0].key,'capture_video_1')
        self.assertIn('Ready for a new take',app.info[0].value)

if __name__=='__main__': unittest.main()
