## 2024-05-22 - Inline Delete Confirmation
**Learning:** For mobile-first Streamlit apps, inline confirmation (replacing the action button with "Confirm"/"Cancel") preserves context better than modals and avoids the jarring full-page overlay effect.
**Action:** Use a state variable (e.g., `confirm_delete_id`) to track which item is being modified and dynamically switch the button layout for that row only.
