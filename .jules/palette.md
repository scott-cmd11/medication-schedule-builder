## 2024-05-23 - Inline Confirmation for Destructive Actions

**Learning:**
In mobile-first Streamlit apps, modal dialogs can be disruptive or harder to manage with pure Python state. Inline confirmation (replacing the action button with "Confirm/Cancel" buttons in the same row) preserves the user's context, especially in long lists like a medication schedule. It avoids the "loss of place" that can happen when a modal triggers a full page refresh or obscures the content being acted upon.

**Action:**
For list-based destructive actions (like deleting an item):
1. Use a unique ID (e.g., `added_at` timestamp) to track which item is in "confirmation mode" in `session_state`.
2. Dynamically adjust `st.columns` ratios for that specific row to accommodate the two buttons (e.g., changing from `[4, 1]` to `[3, 2]`).
3. Use a nested column layout for the buttons if needed, or rely on `AppButton`/`st.button` sizing.
4. Ensure the "Cancel" action simply clears the state ID to restore the original view.
