## 2026-02-04 - [Streamlit Caching & Error Handling]
**Learning:** `st.cache_data` caches the return value, including error tuples if returned. To prevent caching transient API failures, the cached function MUST raise an exception instead of returning an error state.
**Action:** Always separate API fetch logic (which raises exceptions) from UI logic (which catches exceptions and displays errors) when using Streamlit caching.
