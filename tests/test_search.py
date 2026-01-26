import sys
import unittest
from unittest.mock import MagicMock

# Mock streamlit before importing app
mock_st = MagicMock()
# Mock st.cache_data as a pass-through decorator
mock_st.cache_data = lambda func: func
# Mock columns to return iterable
mock_st.columns.side_effect = lambda n, **kwargs: [MagicMock() for _ in range(n)] if isinstance(n, int) else [MagicMock() for _ in n]

# Mock session_state
class SessionState(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value

mock_st.session_state = SessionState()

sys.modules['streamlit'] = mock_st

# Import app after mocking
import app

class TestSearchMedications(unittest.TestCase):
    def test_search_logic(self):
        # 1. Case insensitivity
        # Search for "aspirin" (lowercase), should find ASPIRIN (uppercase in DB)
        results = app.search_medications("aspirin")
        found = any(m['brand_name'] == 'ASPIRIN' for m in results)
        self.assertTrue(found, "Should find ASPIRIN when searching 'aspirin'")

        # 2. Starts-with prioritization
        # "PRO" should find PROZAC (starts with) before CIPRO (contains)
        # Verify PROZAC is in DB and starts with PRO
        # Verify CIPRO is in DB and contains PRO (and ideally doesn't start with it, but CIPRO doesn't start with PRO? Wait. CIPRO starts with CI)
        results = app.search_medications("PRO")
        prozac_idx = -1
        cipro_idx = -1

        # Use first occurrence
        for i, m in enumerate(results):
            if m['brand_name'] == 'PROZAC' and prozac_idx == -1:
                prozac_idx = i
            if m['brand_name'] == 'CIPRO' and cipro_idx == -1:
                cipro_idx = i

        if prozac_idx != -1 and cipro_idx != -1:
            self.assertLess(prozac_idx, cipro_idx, "PROZAC (startswith) should come before CIPRO (contains)")

        # 3. Preservation of order (Stability)
        # Use verified unique items or items with known relative order.
        # PRAVASTATIN (Index ~19) vs PROPRANOLOL (Index ~48)
        # Both start with "PR".
        # Should preserve DB order.
        results = app.search_medications("PR")
        prava_idx = -1
        prop_idx = -1

        for i, m in enumerate(results):
            if m['brand_name'] == 'PRAVASTATIN' and prava_idx == -1:
                prava_idx = i
            if m['brand_name'] == 'PROPRANOLOL' and prop_idx == -1:
                prop_idx = i

        if prava_idx != -1 and prop_idx != -1:
            self.assertLess(prava_idx, prop_idx, "Should preserve DB order for ties (PRAVASTATIN before PROPRANOLOL)")

    def test_performance_assumption(self):
        # Verify that we are not creating new dicts
        # (Though st.cache_data MIGHT serialize/deserialize in real life,
        # the underlying logic function should return original objects for efficiency)

        # We need to find an item in results and check if it IS the item in MEDICATION_DATABASE
        query = "ASPIRIN"
        results = app.search_medications(query)
        if results:
            first_result = results[0]
            # Find it in DB
            db_item = next(m for m in app.MEDICATION_DATABASE if m['brand_name'] == first_result['brand_name'])
            # Identity check
            self.assertIs(first_result, db_item, "Should return reference to original dict, not copy")

if __name__ == '__main__':
    unittest.main()
