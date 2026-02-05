## 2024-05-22 - Caching External API Calls
**Learning:** Streamlit apps re-run the entire script on every interaction. Synchronous external API calls (like Health Canada drug search) block the UI and lead to redundant network requests.
**Action:** Wrap external data fetching logic in functions decorated with `@st.cache_data`. Ensure error states are raised (not returned) to prevent caching failures.
