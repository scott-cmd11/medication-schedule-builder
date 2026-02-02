import sys
import unittest
from unittest.mock import MagicMock
import html

class MockSessionState(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

# Mock streamlit before importing app
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st
sys.modules['streamlit.components.v1'] = MagicMock()

# Configure columns to return list of mocks
def mock_columns(n, gap=None):
    if isinstance(n, int):
        return [MagicMock() for _ in range(n)]
    return [MagicMock() for _ in n]

mock_st.columns.side_effect = mock_columns

# Mock session state
mock_st.session_state = MockSessionState({'med_list': [], 'verification_states': {}})

# Now import the app
import app

class TestXSS(unittest.TestCase):
    def test_generate_preview_html_xss(self):
        # Malicious input
        malicious_name = '<script>alert("XSS")</script>'
        med_list = [{
            'name': malicious_name,
            'strength_value': '10',
            'strength_unit': 'mg',
            'source': 'manual',
            'time_slots': ['Morning'],
            'variable_dosing': False,
            'dose_schedule': None
        }]

        # Generate HTML
        html_output = app.generate_preview_html(med_list)

        # Check if the script tag is ESCAPED (secure)
        self.assertNotIn(malicious_name, html_output)
        self.assertIn(html.escape(malicious_name), html_output)

    def test_generate_calendar_html_xss(self):
        # Malicious input
        malicious_name = '<img src=x onerror=alert(1)>'
        med_list = [{
            'name': malicious_name,
            'strength_value': '10',
            'strength_unit': 'mg',
            'source': 'manual',
            'time_slots': ['Morning'],
            'variable_dosing': False,
            'dose_schedule': None
        }]

        # Generate HTML
        html_output = app.generate_calendar_html(med_list)

        # Check if the payload is ESCAPED (secure)
        self.assertNotIn(malicious_name, html_output)
        self.assertIn(html.escape(malicious_name), html_output)

if __name__ == '__main__':
    unittest.main()
