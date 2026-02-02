import sys
from unittest.mock import MagicMock, patch
import os
import unittest
import requests

# Mock streamlit before importing app
mock_st = MagicMock()

class MockSessionState(dict):
    """Mock session state that supports both dict and attribute access."""
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'MockSessionState' object has no attribute '{key}'")
    def __setattr__(self, key, value):
        self[key] = value

mock_st.session_state = MockSessionState()

def mock_columns(spec, **kwargs):
    """Mock st.columns to return correct number of columns."""
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    # Assume spec is a list/tuple of widths
    return [MagicMock() for _ in range(len(spec))]
mock_st.columns.side_effect = mock_columns

sys.modules['streamlit'] = mock_st

# Mock cache_data to just call the function (pass-through)
def mock_cache_data(**kwargs):
    def decorator(func):
        return func
    return decorator
mock_st.cache_data = mock_cache_data

# Ensure sys.path includes the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app
import app

class TestApiRefactor(unittest.TestCase):
    @patch('requests.get')
    def test_search_health_canada_api_success(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'brand_name': 'Tylenol', 'company_name': 'McNeil'},
            {'brand_name': 'Advil', 'company_name': 'Pfizer'}
        ]
        mock_get.return_value = mock_response

        # Call the function
        results, error = app.search_health_canada_api("Tylenol")

        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['brand_name'], 'Tylenol')
        self.assertIsNone(error)

        # Verify requests.get was called
        mock_get.assert_called()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['timeout'], (5, 60))

    @patch('requests.get')
    def test_search_health_canada_api_failure(self, mock_get):
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        # Call the function
        results, error = app.search_health_canada_api("Tylenol")

        # Verify error handling
        self.assertEqual(results, [])
        self.assertIn("timed out", error)

    @patch('requests.get')
    def test_fetch_health_canada_data_retry(self, mock_get):
        # Test the retry logic in the helper function

        # First call fails with ReadTimeout, second succeeds
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        mock_get.side_effect = [requests.exceptions.ReadTimeout("Timeout"), mock_response]

        # Call the helper directly
        app._fetch_health_canada_data("Tylenol")

        # Verify called twice
        self.assertEqual(mock_get.call_count, 2)
        # Verify second call has longer timeout
        args1, kwargs1 = mock_get.call_args_list[0]
        args2, kwargs2 = mock_get.call_args_list[1]
        self.assertEqual(kwargs1['timeout'], (5, 60))
        self.assertEqual(kwargs2['timeout'], (5, 90))

if __name__ == '__main__':
    unittest.main()
