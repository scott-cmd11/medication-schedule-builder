# Palette's Journal

## 2024-05-22 - Stateful Buttons in Dynamic Lists
**Learning:** In Streamlit, when generating interactive elements (like buttons) inside loops, using the loop index as a key is dangerous if the list can change (e.g., deleting items). It causes state mismatches where the wrong item might be acted upon or the UI updates incorrectly.
**Action:** Always use a stable, unique identifier (like an `added_at` timestamp or a unique ID) as the `key` for widgets generated in loops.

## 2024-05-22 - Consistent Button Styling
**Learning:** Standard Streamlit buttons are limited in styling. Wrapping them in a custom component (like `AppButton`) allows for consistent styling and behavior, but we must ensure we expose necessary properties like `help` (tooltip) to maintain accessibility.
**Action:** When creating wrapper components, strictly define the interface to include accessibility props like `help` strings and ensure they are passed down to the underlying Streamlit widget.
