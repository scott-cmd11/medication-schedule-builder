## 2026-02-04 - Inline Confirmation for Destructive Actions
**Learning:** For lists where context is key (like medication schedules), modal dialogs can be disruptive. An inline confirmation pattern (replacing the action button with "Confirm"/"Cancel") preserves the user's context and visual flow, especially on mobile.
**Action:** Use `st.columns` to dynamically swap action buttons with a confirmation group (Primary Confirm + Secondary Cancel) using a unique ID in session state.
