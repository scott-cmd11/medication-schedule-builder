## 2025-05-21 - Inline Destructive Confirmation
**Learning:** For destructive actions in lists (like delete), users prefer an inline confirmation (replacing the action button with confirm/cancel) over a modal or immediate deletion. This maintains context and prevents accidental data loss without disrupting the flow.
**Action:** Use a session state variable (e.g., `confirm_delete_idx`) to track which item is in 'confirmation mode' and conditionally render the action buttons for that row.
