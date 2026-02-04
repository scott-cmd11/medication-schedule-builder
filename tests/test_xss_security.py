import sys
from unittest.mock import MagicMock
import html

# Mock modules BEFORE they are imported by app.py
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st
sys.modules['streamlit.components.v1'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['fpdf'] = MagicMock()

# Mock session_state
class SessionState(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value

payload = '<script>alert("XSS")</script>'
escaped_payload = html.escape(payload)

session_state = SessionState({
    'med_list': [
        {
            'name': payload,
            'strength_value': 10,
            'strength_unit': 'mg',
            'time_slots': ['Morning'],
            'source': 'manual',
            'variable_dosing': False,
            'added_at': '2023-01-01T00:00:00'
        }
    ],
    'verification_states': {},
    'show_preview_modal': False,
    'selected_medication': None,
    'manual_entry_mode': False,
    'dose_value': 0.0,
    'dose_unit': 'mg',
    'selected_times': [],
    'custom_doses': [],
    'hc_search_ran': False,
    'hc_search_last': "",
    'hc_search_error': "",
    'api_search_results': [],
    'show_hc_search': False,
    'final_ack_check': False
})

mock_st.session_state = session_state

def mock_columns(spec, **kwargs):
    count = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(count)]

mock_st.columns.side_effect = mock_columns
mock_st.expander.return_value.__enter__.return_value = MagicMock()
mock_st.container.return_value.__enter__.return_value = MagicMock()
mock_st.spinner.return_value.__enter__.return_value = MagicMock()
mock_st.set_page_config = MagicMock()

try:
    with open('app.py', 'r') as f:
        code = f.read()

    exec(code, {'__name__': '__main__', 'st': mock_st})
except Exception as e:
    print(f"Execution stopped: {e}")
    import traceback
    traceback.print_exc()

# Check calls to st.markdown
found_vulnerability = False
found_fix = False

print("Checking st.markdown calls...")
for call in mock_st.markdown.call_args_list:
    args, kwargs = call
    if args:
        content = args[0]
        unsafe = kwargs.get('unsafe_allow_html', False)

        if payload in content and unsafe:
            print("VULNERABILITY DETECTED: Found unescaped malicious script in st.markdown with unsafe_allow_html=True")
            found_vulnerability = True

        if escaped_payload in content and unsafe:
            print("FIX VERIFIED: Found escaped payload in st.markdown")
            found_fix = True

if found_vulnerability:
    print("TEST FAILED: Vulnerability still exists.")
    sys.exit(1)
elif found_fix:
    print("TEST PASSED: Vulnerability fixed (payload escaped).")
    sys.exit(0)
else:
    print("TEST INCONCLUSIVE: Neither payload nor escaped payload found (code path might not have been reached).")
    sys.exit(1)
