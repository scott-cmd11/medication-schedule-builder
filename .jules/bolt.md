## 2024-05-23 - Caching Health Canada API
**Learning:** External API calls in Streamlit apps run on every interaction if not cached, leading to severe latency. Using `@st.cache_data` on a helper function (that raises exceptions on failure) is the pattern to fix this.
**Action:** Always wrap `requests.get` in a cached helper for static/quasi-static data sources.
