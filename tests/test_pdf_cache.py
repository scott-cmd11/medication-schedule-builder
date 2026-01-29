import sys
import unittest
from unittest.mock import MagicMock

# 1. Mock modules BEFORE importing app

# Custom SessionState that supports both dict and attribute access
class SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value

# Streamlit mock
st_mock = MagicMock()
st_mock.session_state = SessionState()

# Configure columns to return a list of mocks (unpacker support)
def columns_side_effect(spec, gap="small"):
    # spec can be int or list.
    if isinstance(spec, int):
        count = spec
    else:
        count = len(spec)
    return [MagicMock() for _ in range(count)]

st_mock.columns.side_effect = columns_side_effect

# Configure cache_data to be a decorator that we can verify
def cache_data_decorator(func):
    func._is_cached_by_bolt = True
    return func
st_mock.cache_data = cache_data_decorator

sys.modules['streamlit'] = st_mock
sys.modules['fpdf'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['streamlit_keyup'] = MagicMock()

# 2. Import app
# We catch potential import errors, though mocks should handle most
try:
    import app
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error importing app: {e}")
    sys.exit(1)

import inspect

class TestPdfCache(unittest.TestCase):
    def test_generate_pdf_is_cached(self):
        """Verify that generate_pdf is decorated with @st.cache_data."""
        # We check for the attribute we added in our mock decorator
        is_cached = getattr(app.generate_pdf, '_is_cached_by_bolt', False)
        self.assertTrue(is_cached, "generate_pdf is NOT decorated with @st.cache_data")

    def test_generate_pdf_signature(self):
        """Verify that generate_pdf accepts generation_time."""
        sig = inspect.signature(app.generate_pdf)
        self.assertIn('generation_time', sig.parameters, "generate_pdf does not accept 'generation_time'")

if __name__ == '__main__':
    unittest.main()
