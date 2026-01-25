import sys
from unittest.mock import MagicMock

# 1. Setup Mocks for Streamlit
# We must do this before importing app.py (or executing it)
st_mock = MagicMock()
sys.modules['streamlit'] = st_mock
# Also mock submodules if needed, but MagicMock usually handles children attributes

# 2. Setup Session State
# We need a custom class to mimic Streamlit's session_state which works as both dict and attribute
class SessionState(dict):
    def __getattr__(self, item):
        return self.get(item)
    def __setattr__(self, item, value):
        self[item] = value

# Initialize with our payload
initial_state = {
    'med_list': [
        {
            'name': '<script>alert("XSS")</script>',
            'strength_value': 10,
            'strength_unit': 'mg',
            'time_slots': ['Morning'],
            'source': 'manual',
            'variable_dosing': False,
            'dose_schedule': None
        }
    ],
    'verification_states': {},
    'show_preview_modal': False,
    'final_ack_check': False,
    'api_search_results': [],
    'selected_medication': None,
    'manual_entry_mode': False,
    'dose_value': 0.0,
    'dose_unit': 'mg',
    'selected_times': [],
    'custom_doses': [],
    'hc_search_ran': False,
    'hc_search_last': '',
    'hc_search_error': '',
    'show_hc_search': False
}

st_mock.session_state = SessionState(initial_state)

# 3. Setup context managers for layout elements
# st.columns returns a list of context managers
def mock_columns(spec, **kwargs):
    count = spec if isinstance(spec, int) else len(spec)
    cols = [MagicMock() for _ in range(count)]
    for col in cols:
        col.__enter__.return_value = col
        col.__exit__.return_value = None
    return cols

st_mock.columns.side_effect = mock_columns

# st.container, st.expander, st.spinner are context managers
for ctx_mgr in ['container', 'expander', 'spinner']:
    getattr(st_mock, ctx_mgr).return_value.__enter__.return_value = MagicMock()
    getattr(st_mock, ctx_mgr).return_value.__exit__.return_value = None

# 4. Capture st.markdown calls
markdown_calls = []
def capture_markdown(body, unsafe_allow_html=False):
    markdown_calls.append({'body': body, 'unsafe': unsafe_allow_html})

st_mock.markdown.side_effect = capture_markdown

# 5. Execute app.py
print("Executing app.py with mocks...")
try:
    with open('app.py', 'r') as f:
        code = compile(f.read(), 'app.py', 'exec')
        exec(code, {'__name__': '__main__'})
except Exception as e:
    # It's okay if it fails later, as long as it renders the list
    print(f"App execution stopped: {e}")

# 6. Analyze Results
vulnerable = False
for call in markdown_calls:
    if '<script>alert("XSS")</script>' in call['body'] and call['unsafe']:
        vulnerable = True
        print(f"Found unsafe injection in: {call['body'][:100]}...")

if vulnerable:
    print("VULNERABILITY CONFIRMED: Unescaped script tag found in markdown with unsafe_allow_html=True")
    sys.exit(1)
else:
    print("SECURE: No unescaped script tags found.")
    sys.exit(0)
