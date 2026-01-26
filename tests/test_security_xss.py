import unittest
from unittest.mock import MagicMock
import sys
import datetime

# Mocking dependencies before importing app
class MockSessionState(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'MockSessionState' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
        self.markdown = MagicMock()
        self.set_page_config = MagicMock()
        self.container = MagicMock()

        # Determine columns based on input
        def columns_mock(spec, **kwargs):
            if isinstance(spec, int):
                return [MagicMock() for _ in range(spec)]
            else:
                return [MagicMock() for _ in range(len(spec))]

        self.columns = MagicMock(side_effect=columns_mock)
        self.button = MagicMock()
        self.text_input = MagicMock()
        self.selectbox = MagicMock()
        self.number_input = MagicMock()
        self.checkbox = MagicMock()
        self.expander = MagicMock()
        self.radio = MagicMock()
        self.toast = MagicMock()
        self.spinner = MagicMock()
        self.cache_data = lambda func: func

    def __getattr__(self, name):
        return MagicMock()

sys.modules['streamlit'] = MockStreamlit()
sys.modules['streamlit.components.v1'] = MagicMock()
sys.modules['fpdf'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['pandas'] = MagicMock()

# Import app after mocking
import app

class TestXSSVulnerability(unittest.TestCase):
    def test_generate_preview_html_xss(self):
        """Test that generate_preview_html escapes HTML in medication names."""

        # Payload that would be dangerous if not escaped
        malicious_name = "<script>alert('xss')</script>"
        malicious_unit = "<b>mg</b>"

        med_list = [{
            'name': malicious_name,
            'strength_value': 10,
            'strength_unit': malicious_unit,
            'source': 'manual',
            'time_slots': ['Morning']
        }]

        html_output = app.generate_preview_html(med_list)

        print("\nHTML Output snippet:", html_output[:200])

        if "<script>" in html_output:
            print("VULNERABILITY CONFIRMED: <script> tag found in output")
        else:
            print("SAFE: <script> tag NOT found in output")

        self.assertNotIn("<script>", html_output, "XSS Vulnerability: Raw <script> tag found in HTML output")
        self.assertIn("&lt;script&gt;", html_output, "Escaping check: Expected escaped script tag")

    def test_generate_calendar_html_xss(self):
        """Test that generate_calendar_html escapes HTML."""
        malicious_name = "\"><img src=x onerror=alert(1)>"

        med_list = [{
            'name': malicious_name,
            'strength_value': 10,
            'strength_unit': 'mg',
            'source': 'manual',
            'time_slots': ['Morning'],
            'variable_dosing': False
        }]

        html_output = app.generate_calendar_html(med_list)

        self.assertNotIn("<img", html_output, "XSS Vulnerability: Raw <img tag found in calendar output")
        self.assertIn("&lt;img", html_output, "Escaping check: Expected escaped img tag")

if __name__ == '__main__':
    unittest.main()
