# Palette's UX Journal

## 2024-05-22 - Safety in Medication Lists
**Learning:** In list-building apps where order and precision matter (like medication schedules), immediate destruction (delete) without confirmation is a dangerous pattern. Users lose context if the list shifts unexpectedly.
**Action:** Implement "soft" delete confirmations inline. Use unique IDs (like timestamps) for list items instead of array indices to ensure UI state (like "confirm delete") sticks to the correct item even if the list order changes.

## 2024-05-22 - Accessibility of Repetitive Actions
**Learning:** Repeating generic labels like "Verified" or "Delete" in a list is poor for screen reader users who may navigate by button/checkbox type.
**Action:** Always inject the specific item name into the accessible label or tooltip (e.g., "Verify Tylenol" instead of just "Verified"). This provides necessary context without cluttering the visual UI.
