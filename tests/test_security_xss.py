import unittest
from unittest.mock import MagicMock
import sys
import os

# Add root directory to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st

# Configure session state to act like a dict
# It needs to support item access and attribute access in some cases in Streamlit,
# but in this app it seems to use st.session_state.med_list and st.session_state['med_list']
# We can use a real dict for simplicity, but wrap it in a Mock if needed for attribute access.
# Let's use a class that behaves like both.
class SessionState(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value

mock_st.session_state = SessionState()
mock_st.session_state.med_list = []
mock_st.session_state.verification_states = {}

# Configure st.columns to return a list of mocks
def columns_side_effect(spec, *args, **kwargs):
    count = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(count)]
mock_st.columns.side_effect = columns_side_effect

# Mock requests, fpdf, pandas
sys.modules['requests'] = MagicMock()
sys.modules['fpdf'] = MagicMock()
sys.modules['pandas'] = MagicMock()

# Import app (this will execute the script, but with mocks)
try:
    import app
except Exception as e:
    print(f"Warning: app import caused exception: {e}")
    # We might continue if the functions are defined before the crash
    pass

class TestSecurityXSS(unittest.TestCase):
    def test_generate_calendar_html_sanitization(self):
        """Test that generate_calendar_html sanitizes inputs."""
        med_list = [{
            'name': '<script>alert("XSS")</script>',
            'strength_value': 5,
            'strength_unit': 'mg" onmouseover="alert(1)',
            'time_slots': ['Morning'],
            'source': 'manual',
            'variable_dosing': False
        }]

        html_out = app.generate_calendar_html(med_list)

        # Verify malicious tags are escaped
        self.assertNotIn('<script>', html_out)
        self.assertIn('&lt;script&gt;', html_out)

        # Check that attributes are escaped
        # "mg" onmouseover="alert(1)" -> mg&quot; onmouseover=&quot;alert(1)&quot;
        # The surrounding HTML is <div class="med-dose">... {unit}...</div>
        # So quotes are html encoded.
        self.assertIn('mg&quot; onmouseover=&quot;alert(1)', html_out)

    def test_generate_preview_html_sanitization(self):
        """Test that generate_preview_html sanitizes inputs."""
        med_list = [{
            'name': '<img src=x onerror=alert(1)>',
            'strength_value': '10',
            'strength_unit': '<i>mg</i>',
            'time_slots': ['Morning'],
            'source': 'manual'
        }]

        html_out = app.generate_preview_html(med_list)

        self.assertNotIn('<img', html_out)
        self.assertIn('&lt;img', html_out)
        self.assertNotIn('<i>', html_out)
        self.assertIn('&lt;i&gt;', html_out)

if __name__ == '__main__':
    unittest.main()
