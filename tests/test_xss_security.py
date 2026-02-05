import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Setup Mocks BEFORE importing app
class MockSessionState(dict):
    """Mocks Streamlit session state allowing dict and attribute access."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

st_mock = MagicMock()
st_mock.session_state = MockSessionState()

# Mock st.columns to return a list of mocks so unpacking works
def mock_columns(spec, *args, **kwargs):
    count = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(count)]

st_mock.columns.side_effect = mock_columns

sys.modules["streamlit"] = st_mock
sys.modules["requests"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["fpdf"] = MagicMock()

# 2. Import app
try:
    import app
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

class TestXSSSecurity(unittest.TestCase):
    def test_generate_calendar_html_xss_protection(self):
        """Test that generate_calendar_html escapes malicious input."""
        malicious_name = "<script>alert('xss')</script>"
        malicious_unit = "mg<img src=x>"
        malicious_dose = "<iframe src=x>"

        # Expected escaped versions
        escaped_name = "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        escaped_unit = "mg&lt;img src=x&gt;"
        escaped_dose = "&lt;iframe src=x&gt;"

        malicious_med = {
            "name": malicious_name,
            "strength_value": malicious_dose, # Injected here
            "strength_unit": malicious_unit,
            "time_slots": ["Morning"],
            "source": "manual",
            "variable_dosing": False,
            "dose_schedule": None
        }

        # Generate HTML
        html = app.generate_calendar_html([malicious_med])

        # Assert RAW tag is NOT present
        self.assertNotIn(malicious_name, html, "VULNERABILITY DETECTED: Raw script tag found in calendar HTML (Name)")
        self.assertNotIn(malicious_unit, html, "VULNERABILITY DETECTED: Raw IMG tag found in calendar HTML (Unit)")
        self.assertNotIn(malicious_dose, html, "VULNERABILITY DETECTED: Raw IFRAME tag found in calendar HTML (Dose)")

        # Assert ESCAPED version IS present
        self.assertIn(escaped_name, html, "Escaped name not found in output")
        self.assertIn(escaped_unit, html, "Escaped unit not found in output")
        self.assertIn(escaped_dose, html, "Escaped dose not found in output")

    def test_generate_preview_html_xss_protection(self):
        """Test that generate_preview_html escapes malicious input."""
        malicious_name = "<script>alert('preview')</script>"
        malicious_dose = "<img src=x>"

        escaped_name = "&lt;script&gt;alert(&#x27;preview&#x27;)&lt;/script&gt;"
        escaped_dose = "&lt;img src=x&gt;"

        malicious_med = {
            "name": malicious_name,
            "strength_value": malicious_dose,
            "strength_unit": "mg",
            "time_slots": ["Morning"],
            "source": "manual",
        }

        html = app.generate_preview_html([malicious_med])

        self.assertNotIn(malicious_name, html, "VULNERABILITY DETECTED: Raw script tag found in preview HTML")
        self.assertNotIn(malicious_dose, html, "VULNERABILITY DETECTED: Raw IMG tag found in preview HTML (Dose)")

        self.assertIn(escaped_name, html, "Escaped name not found in preview output")
        self.assertIn(escaped_dose, html, "Escaped dose not found in preview output")

if __name__ == "__main__":
    unittest.main()
