import sys
from unittest.mock import MagicMock

# Mock streamlit before importing app
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st

# Configure mock behavior for module-level calls
def mock_columns(spec, gap=None, **kwargs):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    return [MagicMock() for _ in spec]

mock_st.columns.side_effect = mock_columns

# Mock session_state
class MockSessionState(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

# Initialize with expected keys
mock_state = MockSessionState()
mock_state['med_list'] = []
mock_state['verification_states'] = {}
mock_state['show_hc_search'] = False

mock_st.session_state = mock_state
mock_st.button.return_value = False

import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app

def test_xss_in_preview_html():
    malicious_input = "<script>alert('xss')</script>"
    med_list = [{
        'name': malicious_input,
        'strength_value': '10',
        'strength_unit': 'mg',
        'time_slots': ['Morning'],
        'source': 'manual'
    }]

    html = app.generate_preview_html(med_list)

    if malicious_input in html:
        print("VULNERABILITY CONFIRMED: <script> tag found in HTML output")
    else:
        print("SAFE: Malicious input was escaped or not found")
        if "&lt;script&gt;" in html:
             print("VERIFIED: Input was properly escaped.")

def test_xss_in_calendar_html():
    malicious_input = "<img src=x onerror=alert(1)>"
    med_list = [{
        'name': malicious_input,
        'strength_value': '10',
        'strength_unit': 'mg',
        'time_slots': ['Morning'],
        'source': 'manual',
        'variable_dosing': False,
        'dose_schedule': None
    }]

    html = app.generate_calendar_html(med_list)

    if malicious_input in html:
        print("VULNERABILITY CONFIRMED: <img> tag found in Calendar HTML output")
    else:
        print("SAFE: Malicious input was escaped or not found")
        if "&lt;img" in html:
             print("VERIFIED: Input was properly escaped.")

def test_valid_input_rendering():
    med_list = [{
        'name': "Aspirin",
        'strength_value': '81',
        'strength_unit': 'mg',
        'time_slots': ['Morning'],
        'source': 'manual',
        'variable_dosing': False,
        'dose_schedule': None
    }]

    html = app.generate_calendar_html(med_list)

    if "Aspirin" in html and "81 mg" in html:
        print("VALID INPUT: Rendered correctly.")
    else:
        print("VALID INPUT: Failed to render expected text.")

if __name__ == "__main__":
    try:
        print("Testing generate_preview_html...")
        test_xss_in_preview_html()
        print("\nTesting generate_calendar_html...")
        test_xss_in_calendar_html()
        print("\nTesting valid input...")
        test_valid_input_rendering()
    except Exception as e:
        print(f"Test failed with exception: {e}")
