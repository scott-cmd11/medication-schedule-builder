import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to sys.path so we can import app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestXSS(unittest.TestCase):
    def setUp(self):
        # Create a fresh mock for streamlit
        self.st_mock = MagicMock()
        sys.modules['streamlit'] = self.st_mock

        # Setup st.columns to return a list of mocks
        def columns_side_effect(spec, gap=None, **kwargs):
            if isinstance(spec, int):
                count = spec
            else:
                count = len(spec)
            return [MagicMock() for _ in range(count)]

        self.st_mock.columns.side_effect = columns_side_effect

        # Setup session state behavior
        class SessionState(dict):
            def __getattr__(self, key):
                return self.get(key)
            def __setattr__(self, key, value):
                self[key] = value

        self.session_state = SessionState()
        self.st_mock.session_state = self.session_state

    def test_medication_list_xss(self):
        # Inject a malicious medication
        malicious_name = "<script>alert('XSS')</script>"

        # Pre-populate session state
        self.session_state['med_list'] = [{
            'name': malicious_name,
            'strength_value': 10,
            'strength_unit': 'mg',
            'time_slots': ['Morning'],
            'source': 'manual',
            'variable_dosing': False
        }]
        self.session_state['verification_states'] = {}

        # Mock other dependencies
        sys.modules['requests'] = MagicMock()
        sys.modules['pandas'] = MagicMock()
        sys.modules['fpdf'] = MagicMock()

        # Clean up app from sys.modules if it exists
        if 'app' in sys.modules:
            del sys.modules['app']

        # Run the app
        try:
            import app
        except Exception as e:
            self.fail(f"App failed to run with mocks: {e}")

        # Check st.markdown calls
        found_escaped = False
        found_raw = False

        for call in self.st_mock.markdown.call_args_list:
            args, _ = call
            if args:
                html_content = args[0]
                # Check for raw payload
                if malicious_name in html_content:
                    found_raw = True

                # Check for escaped payload
                if "&lt;script&gt;" in html_content:
                    found_escaped = True

        # Assertions
        self.assertFalse(found_raw, "FAIL: Found raw XSS payload in st.markdown calls! Application is vulnerable.")
        self.assertTrue(found_escaped, "FAIL: Did not find escaped payload in st.markdown calls. Rendering might be missing or logic changed.")

if __name__ == '__main__':
    unittest.main()
