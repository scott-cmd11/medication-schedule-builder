## 2024-05-22 - Delete Confirmation Pattern
**Learning:** Users often click destructive actions (like delete icons) by mistake, especially in list views. Immediate deletion causes frustration.
**Action:** Implemented an inline confirmation pattern using session state to track the item being deleted. Replaced the single icon button with "Yes" (Primary) and "No" (Secondary) buttons, temporarily adjusting the column layout to accommodate them. This keeps the user in context without a modal popup.
