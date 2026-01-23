## 2025-05-23 - Delete Confirmation for Destructive Actions
**Learning:** In applications where data modification (like deletion) triggers a global reset of verification states (a safety feature), accidental deletion is extremely costly for the user.
**Action:** Always implement a confirmation step (e.g., inline toggle, modal) for destructive actions that have widespread side effects, to prevent user frustration and data loss.
