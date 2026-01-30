import unittest
from unittest.mock import MagicMock, patch
import sys
import html as html_lib

# Create a mock for streamlit
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st

# Setup session state mock to behave like a dict and object
class SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return MagicMock() # Return mock for unknown keys
    def __setattr__(self, key, value):
        self[key] = value

mock_session_state = SessionState()
mock_st.session_state = mock_session_state

# Improve st.columns mock
def columns_side_effect(spec, **kwargs):
    if isinstance(spec, int):
        count = spec
    else:
        count = len(spec)
    return [MagicMock() for _ in range(count)]

mock_st.columns.side_effect = columns_side_effect
mock_st.container.return_value.__enter__.return_value = MagicMock()
mock_st.expander.return_value.__enter__.return_value = MagicMock()
mock_st.spinner.return_value.__enter__.return_value = MagicMock()

# Mock extra dependencies
sys.modules['fpdf'] = MagicMock()

class TestXSS(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        mock_st.reset_mock()
        mock_st.markdown.reset_mock()

        # Reset session state
        mock_session_state.clear()
        mock_session_state['med_list'] = []
        mock_session_state['verification_states'] = {}
        mock_session_state['selected_medication'] = None # Ensure we don't enter "Edit Mode"
        mock_session_state['manual_entry_mode'] = False
        mock_session_state['show_hc_search'] = False
        mock_session_state['dose_value'] = 0.0
        mock_session_state['selected_times'] = []

    def test_vulnerable_med_rendering(self):
        # Inject malicious payload
        malicious_payload = "<script>alert('XSS')</script>"

        # Pre-populate session state to trigger rendering logic in the list loop
        mock_session_state['med_list'] = [{
            'name': malicious_payload,
            'strength_value': '10',
            'strength_unit': 'mg',
            'time_slots': ['Morning'],
            'source': 'manual',
            'added_at': '2023-01-01',
            'variable_dosing': False,
            'dose_schedule': None
        }]

        # Read code
        with open('app.py', 'r') as f:
            code = f.read()

        # Run the code
        try:
            exec(code, {'__name__': '__main__'})
        except Exception as e:
            # print(f"Execution error (ignored): {e}")
            pass

        # Check if st.markdown was called with the payload unescaped
        found_vulnerability = False
        for call in mock_st.markdown.call_args_list:
            args, kwargs = call
            if args:
                content = args[0]
                unsafe = kwargs.get('unsafe_allow_html', False)

                # Check if malicious payload exists AND is NOT escaped
                # If it's escaped, it looks like &lt;script&gt;...
                # If unescaped, it looks like <script>...

                if malicious_payload in content and unsafe:
                    found_vulnerability = True
                    break

        # We expect the vulnerability to be ABSENT (escaped)
        self.assertFalse(found_vulnerability, "XSS Vulnerability FOUND: Malicious payload rendered unescaped!")

if __name__ == '__main__':
    # Add project root to sys.path so imports work if needed
    sys.path.append('.')
    unittest.main()
