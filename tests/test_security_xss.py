import sys
from unittest.mock import MagicMock

# Create a robust mock for streamlit
st_mock = MagicMock()

# session_state mock
st_mock.session_state = {}
# Allow item access to session_state
# We need a custom class for session_state to support both attribute and item access if needed
# But for now, app.py uses st.session_state['key'] or .get or .key
# The simplest way is to make it a dict but also support attribute access?
# Actually app.py seems to mostly use dictionary access or st.session_state.prop.
# Let's make it a MagicMock that behaves like a dict.

class SessionStateMock(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

st_mock.session_state = SessionStateMock()
# Pre-populate necessary session keys to avoid key errors during import execution
st_mock.session_state.med_list = []
st_mock.session_state.verification_states = {}
st_mock.session_state.selected_medication = None
st_mock.session_state.manual_entry_mode = False
st_mock.session_state.dose_value = 0.0
st_mock.session_state.dose_unit = "mg"
st_mock.session_state.selected_times = []
st_mock.session_state.custom_doses = []
st_mock.session_state.hc_search_ran = False
st_mock.session_state.hc_search_last = ""
st_mock.session_state.hc_search_error = ""
st_mock.session_state.show_preview_modal = False
st_mock.session_state.final_ack_check = False
st_mock.session_state.api_search_results = []
st_mock.session_state.show_hc_search = False


def columns_mock(spec, *args, **kwargs):
    if isinstance(spec, int):
        count = spec
    else:
        count = len(spec)
    return [MagicMock() for _ in range(count)]

st_mock.columns.side_effect = columns_mock
st_mock.container.return_value.__enter__.return_value = MagicMock()
st_mock.expander.return_value.__enter__.return_value = MagicMock()
st_mock.spinner.return_value.__enter__.return_value = MagicMock()

sys.modules['streamlit'] = st_mock
sys.modules['streamlit_keyup'] = MagicMock()

# Now import app
import app
import html

def test_xss_in_preview_html():
    malicious_input = "<script>alert('XSS')</script>"
    med_list = [{
        'name': malicious_input,
        'strength_value': '10',
        'strength_unit': 'mg',
        'time_slots': ['Morning'],
        'source': 'manual'
    }]

    html_output = app.generate_preview_html(med_list)

    # print(f"DEBUG: Output snippet: {html_output[:200]}...")

    # Check if the malicious script is present as-is
    if malicious_input in html_output:
        print("VULNERABILITY FOUND: Script tag found in HTML output")
    else:
        print("SAFE: Script tag not found (likely escaped)")

    # Check for escaped version
    escaped_input = html.escape(malicious_input)
    if escaped_input in html_output:
        print("VERIFIED: Input is escaped")
    else:
        print("NOT ESCAPED properly or format different")

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

    html_output = app.generate_calendar_html(med_list)

    if malicious_input in html_output:
        print("VULNERABILITY FOUND (Calendar): Script tag found in HTML output")
    else:
        print("SAFE (Calendar): Script tag not found")

if __name__ == "__main__":
    print("Running XSS tests...")
    test_xss_in_preview_html()
    test_xss_in_calendar_html()
