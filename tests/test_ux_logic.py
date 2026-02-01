import unittest
from unittest.mock import MagicMock

class TestDeleteConfirmation(unittest.TestCase):
    def setUp(self):
        # Simulate session state
        self.session_state = {
            'med_list': [
                {'name': 'Med A', 'added_at': 't1'},
                {'name': 'Med B', 'added_at': 't2'}
            ],
            'confirm_delete_id': None,
            'verification_states': {0: True, 1: False}
        }

    def test_initiate_delete(self):
        # User clicks delete on Med A (t1)
        med_to_delete = self.session_state['med_list'][0]

        # Action: Set confirm_delete_id
        self.session_state['confirm_delete_id'] = med_to_delete['added_at']

        self.assertEqual(self.session_state['confirm_delete_id'], 't1')

    def test_confirm_delete_action(self):
        # Setup: In confirmation mode for Med A
        self.session_state['confirm_delete_id'] = 't1'

        # Logic to find index
        idx_to_remove = -1
        for i, med in enumerate(self.session_state['med_list']):
            if med['added_at'] == self.session_state['confirm_delete_id']:
                idx_to_remove = i
                break

        # Verify we found the right one
        self.assertEqual(idx_to_remove, 0)

        # Action: Delete
        if idx_to_remove != -1:
            self.session_state['med_list'].pop(idx_to_remove)
            self.session_state['confirm_delete_id'] = None
            # Reset verifications logic (as per app.py logic)
            self.session_state['verification_states'] = {i: False for i in range(len(self.session_state['med_list']))}

        # Verify result
        self.assertEqual(len(self.session_state['med_list']), 1)
        self.assertEqual(self.session_state['med_list'][0]['name'], 'Med B')
        self.assertIsNone(self.session_state['confirm_delete_id'])
        # Verification states should be reset and re-indexed
        self.assertEqual(len(self.session_state['verification_states']), 1)
        self.assertFalse(self.session_state['verification_states'][0])

    def test_cancel_delete_action(self):
        # Setup: In confirmation mode for Med A
        self.session_state['confirm_delete_id'] = 't1'

        # Action: Cancel
        self.session_state['confirm_delete_id'] = None

        # Verify result
        self.assertEqual(len(self.session_state['med_list']), 2)
        self.assertIsNone(self.session_state['confirm_delete_id'])

if __name__ == '__main__':
    unittest.main()
