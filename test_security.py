import sys
from unittest.mock import MagicMock

# Mock streamlit
mock_st = MagicMock()
# We need session_state to be a dict-like object
class MockSessionState(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

mock_st.session_state = MockSessionState()

def mock_columns(*args, **kwargs):
    count = 1
    if args:
        spec = args[0]
        if isinstance(spec, int):
            count = spec
        elif isinstance(spec, (list, tuple)):
            count = len(spec)
    elif 'spec' in kwargs:
        spec = kwargs['spec']
        if isinstance(spec, int):
            count = spec
        elif isinstance(spec, (list, tuple)):
            count = len(spec)
    return [MagicMock() for _ in range(count)]

mock_st.columns.side_effect = mock_columns

sys.modules['streamlit'] = mock_st

# Global app variable
app = None

# Now import app
try:
    import app
    app = sys.modules['app']
except Exception as e:
    print(f"Warning: app import encountered an error: {e}")
    if 'app' in sys.modules:
        app = sys.modules['app']

def test_generate_preview_html():
    print("\n--- Testing generate_preview_html ---")
    if not app:
        print("Error: app module not loaded.")
        return False

    malicious_med = {
        'name': '<script>alert("xss")</script>',
        'strength_value': 10,
        'strength_unit': 'mg',
        'source': 'manual',
        'time_slots': ['Morning']
    }

    # Run without try-except to see full traceback if it fails
    html_output = app.generate_preview_html([malicious_med])

    if '<script>alert("xss")</script>' in html_output:
        print("FAIL: XSS payload found in preview HTML")
        return False
    elif '&lt;script&gt;' in html_output:
        print("PASS: XSS payload escaped in preview HTML")
        return True
    else:
        print("WARNING: Payload not found in expected form. Output snippet:")
        print(html_output)
        return False

def test_generate_calendar_html():
    print("\n--- Testing generate_calendar_html ---")
    if not app:
        print("Error: app module not loaded.")
        return False

    malicious_med = {
        'name': '<script>alert("cal")</script>',
        'strength_value': 10,
        'strength_unit': 'mg',
        'source': 'manual',
        'time_slots': ['Morning'],
        'variable_dosing': False
    }

    # Run without try-except to see full traceback if it fails
    html_output = app.generate_calendar_html([malicious_med])

    if '<script>alert("cal")</script>' in html_output:
        print("FAIL: XSS payload found in calendar HTML")
        return False
    elif '&lt;script&gt;' in html_output:
        print("PASS: XSS payload escaped in calendar HTML")
        return True
    else:
        print("WARNING: Payload not found in expected form. Output snippet:")
        print(html_output)
        return False

if __name__ == "__main__":
    print("Testing XSS vulnerabilities...")
    try:
        preview_safe = test_generate_preview_html()
        calendar_safe = test_generate_calendar_html()

        if preview_safe and calendar_safe:
            print("\nALL TESTS PASSED: Input is properly escaped.")
            sys.exit(0)
        else:
            print("\nTESTS FAILED: Input is NOT properly escaped.")
            sys.exit(1)
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
