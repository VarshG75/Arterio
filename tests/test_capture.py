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

class CaptureInvalidationTests(unittest.TestCase):
    def test_explicit_upload_removal_clears_previous_result(self):
        code=f"import sys\nsys.path.insert(0, {str(ROOT / 'app_and_ml')!r})\nfrom views.capture import upload_changed\nupload_changed('capture_video_0')"
        app=AppTest.from_string(code)
        app.session_state['capture_video_0']=None
        app.session_state['telemetry_computed']=True
        app.session_state['telemetry_data']={'old':True}
        app.session_state['analysis_result']={'quality':'good'}
        app.session_state['upload_id']='old'
        app.run()
        self.assertFalse(app.exception, app.exception)
        self.assertFalse(app.session_state['telemetry_computed'])
        self.assertEqual(app.session_state['telemetry_data'],{})
        self.assertNotIn('analysis_result',app.session_state)
        self.assertNotIn('upload_id',app.session_state)

if __name__=='__main__': unittest.main()
