import sys
import os
from unittest.mock import MagicMock

# Ensure we can import app.py from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Mock streamlit BEFORE importing app
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st

# Mock session_state to behave like a dict AND an object
class SessionState(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

# Initialize session state with a malicious payload
mock_session_state = SessionState()
mock_st.session_state = mock_session_state

# Pre-populate session state to trigger the rendering logic in app.py
# We want to trigger the "Patient Medications" list rendering.
# This requires `med_list` to be populated.
malicious_name = "<script>alert('XSS')</script>"
mock_session_state.med_list = [
    {
        'name': malicious_name,
        'strength_value': 10,
        'strength_unit': 'mg',
        'time_slots': ['Morning'],
        'source': 'manual',
        'variable_dosing': False,
        'added_at': '2023-01-01T00:00:00'
    }
]
mock_session_state.verification_states = {0: False}

# Other required session state keys to avoid KeyErrors during app execution
mock_session_state.selected_medication = None
mock_session_state.manual_entry_mode = False
mock_session_state.dose_value = 0.0
mock_session_state.dose_unit = "mg"
mock_session_state.selected_times = []
mock_session_state.custom_doses = []
mock_session_state.show_hc_search = False
mock_session_state.hc_search_ran = False
mock_session_state.show_preview_modal = False
mock_session_state.api_search_results = [] # Required for search logic
mock_session_state.final_ack_check = False

# Mock st.columns to return a list of mocks (unpacker support)
def mock_columns(spec, **kwargs):
    count = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(count)]

mock_st.columns.side_effect = mock_columns
mock_st.container.return_value.__enter__.return_value = MagicMock()
mock_st.expander.return_value.__enter__.return_value = MagicMock()

# 2. Import app to run it
import app

def test_xss_in_med_list():
    """
    Verify that the malicious name is ESCAPED before being passed to st.markdown.
    """
    import html
    escaped_name = html.escape(malicious_name)

    found_raw_xss = False
    found_escaped_xss = False

    # Iterate through all calls to st.markdown
    for call in mock_st.markdown.call_args_list:
        args, kwargs = call
        if not args:
            continue

        html_content = args[0]
        unsafe_allow = kwargs.get('unsafe_allow_html', False)

        if unsafe_allow:
            if malicious_name in html_content:
                found_raw_xss = True
            if escaped_name in html_content:
                found_escaped_xss = True

    assert not found_raw_xss, "Vulnerability STILL PRESENT: Raw malicious script tag found in st.markdown call."
    assert found_escaped_xss, "Fix NOT VERIFIED: Escaped version of the script tag was not found (maybe the rendering logic changed?)"

if __name__ == "__main__":
    test_xss_in_med_list()
    print("Test passed: Vulnerability fixed!")
