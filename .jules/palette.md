## 2024-05-22 - Inline Confirmation for Destructive Actions
**Learning:** In mobile-first Streamlit apps, immediate execution of destructive actions (like delete) via icon buttons can lead to accidental data loss due to touch targets. Modal dialogs can be jarring or lose context.
**Action:** Implement inline confirmation patterns where the action button expands or replaces the row with "Confirm/Cancel" options. This maintains context (user sees exactly what row they are deleting) and prevents accidental taps without blocking the entire UI.
