## 2024-05-23 - Streamlit Caching Strategy
**Learning:** Streamlit apps re-run the entire script on every interaction. Expensive operations like PDF generation inside the render loop can cause significant UI lag, especially in modals where users might interact with other elements (like checkboxes) without changing the data that drives the expensive operation.
**Action:** Use `@st.cache_data` for expensive output-generation functions like PDF creation, ensuring that the cache keys (arguments) correctly capture all dependencies (e.g., the medication list) so the cache invalidates only when necessary.

## 2024-05-23 - Inline Logic vs Cached Functions
**Learning:** Logic duplicated inline (like search loops) misses out on optimizations applied to the original function (like sorting or casing efficiency) and cannot be cached. Refactoring inline logic to use centralized functions improves both performance (via caching) and consistency.
**Action:** Identify and replace inline logic that duplicates existing helper functions, especially in render loops.
