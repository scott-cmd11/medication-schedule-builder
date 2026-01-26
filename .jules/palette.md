## 2024-05-23 - Inline Delete Confirmation
**Learning:** Destructive actions in list views (like deleting a medication) are prone to accidental clicks, especially on mobile. Modal dialogs can be heavy in Streamlit.
**Action:** Implement an inline confirmation pattern: upon clicking delete, swap the action buttons for "Cancel" and "Confirm" within the same list item row. Use a session state variable (e.g., `confirm_delete_id`) to track which item is in confirmation mode.
