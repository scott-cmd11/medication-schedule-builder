import unittest
import sys
from unittest.mock import MagicMock

# Mock streamlit before importing app
class SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value

mock_st = MagicMock()
mock_st.session_state = SessionState()
mock_st.columns.side_effect = lambda spec, **kwargs: [MagicMock() for _ in range(spec)] if isinstance(spec, int) else [MagicMock() for _ in spec]

mock_container = MagicMock()
mock_st.container.return_value = mock_container
mock_container.__enter__.return_value = mock_container

mock_expander = MagicMock()
mock_st.expander.return_value = mock_expander
mock_expander.__enter__.return_value = mock_expander

mock_spinner = MagicMock()
mock_st.spinner.return_value = mock_spinner
mock_spinner.__enter__.return_value = mock_spinner

sys.modules["streamlit"] = mock_st
sys.modules["streamlit.components.v1"] = MagicMock()
sys.modules["streamlit_keyup"] = MagicMock()

# Import app logic
try:
    import app
except ImportError:
    # If app import fails due to dependencies not being installed in test environment, we skip
    app = None

class TestSecurity(unittest.TestCase):
    def setUp(self):
        if app is None:
            self.skipTest("App module could not be imported")

    def test_generate_preview_html_xss(self):
        malicious_med = {
            "name": "<script>alert(1)</script>",
            "brand_name": "<script>alert(1)</script>",
            "strength_value": "10",
            "strength_unit": "mg",
            "time_slots": ["Morning"],
            "source": "manual",
            "variable_dosing": False,
            "dose_schedule": None
        }

        html_output = app.generate_preview_html([malicious_med])

        self.assertNotIn("<script>", html_output)
        self.assertIn("&lt;script&gt;", html_output)

    def test_generate_calendar_html_xss(self):
        malicious_med = {
            "name": "<script>alert(1)</script>",
            "brand_name": "<script>alert(1)</script>",
            "strength_value": "10",
            "strength_unit": "mg",
            "time_slots": ["Morning"],
            "source": "manual",
            "variable_dosing": False,
            "dose_schedule": None
        }

        html_output = app.generate_calendar_html([malicious_med])

        self.assertNotIn("<script>", html_output)
        self.assertIn("&lt;script&gt;", html_output)

if __name__ == "__main__":
    unittest.main()
