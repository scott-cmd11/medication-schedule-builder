## 2024-05-23 - Caching External APIs and Compute
**Learning:** Expensive operations like external API calls (Health Canada) and PDF generation are bottlenecks in Streamlit apps because they block the main thread and run on every interaction if not cached. Streamlit's `@st.cache_data` is essential for these.
**Action:** Always wrap network calls and heavy compute functions with `@st.cache_data` or `@st.cache_resource` in Streamlit.
