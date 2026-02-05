## 2024-05-22 - Inline Confirmation for Streamlit Lists
**Learning:** For destructive actions in dynamic lists (like deleting a medication), inline confirmation that temporarily replaces the action buttons is superior to modals or global confirmations. It maintains context, reduces layout shifts, and is easily managed via `st.session_state` tracking a unique ID (e.g., `confirm_delete_id`).
**Action:** Prefer inline state toggles for micro-interactions on list items over separate dialogs.
