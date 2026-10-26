"""Refreshes and URL changes keep the intended page selected."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'app_and_ml/app.py'
PAGES = {
    'Telemetry': 'telemetry', 'Heart Explorer': 'heart-explorer',
    'Cohort Analytics': 'cohort', 'Clinical Docs': 'clinical-docs',
    'Architecture': 'architecture',
}


class NavigationTests(unittest.TestCase):
    def test_refresh_selects_each_route(self):
        for name, slug in PAGES.items():
            with self.subTest(page=name):
                app = AppTest.from_file(str(APP))
                app.query_params['page'] = slug
                app.run()
                self.assertFalse(app.exception, app.exception)
                self.assertEqual(app.radio[0].value, name)
                self.assertEqual(app.query_params['page'], [slug])

    def test_navigation_and_widget_rerun_preserve_route(self):
        app = AppTest.from_file(str(APP)).run()
        app.radio[0].set_value('Heart Explorer').run()
        self.assertEqual(app.query_params['page'], ['heart-explorer'])
        app.run()
        self.assertEqual(app.radio[0].value, 'Heart Explorer')
        app.query_params['page'] = 'architecture'
        app.run()
        self.assertFalse(app.exception, app.exception)
        self.assertEqual(app.radio[0].value, 'Architecture')

    def test_unknown_route_returns_to_telemetry(self):
        app = AppTest.from_file(str(APP))
        app.query_params['page'] = 'missing'
        app.run()
        self.assertFalse(app.exception, app.exception)
        self.assertEqual(app.radio[0].value, 'Telemetry')
        self.assertEqual(app.query_params['page'], ['telemetry'])


if __name__ == '__main__':
    unittest.main()
