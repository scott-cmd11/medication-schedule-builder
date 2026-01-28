## 2024-05-23 - [Streamlit Stored XSS]
**Vulnerability:** User input (medication names) was directly interpolated into HTML strings passed to `st.markdown(..., unsafe_allow_html=True)`.
**Learning:** Streamlit apps often rely on `unsafe_allow_html=True` for custom styling (like cards/badges), creating a high risk of stored XSS if dynamic data isn't rigorously sanitized.
**Prevention:** Always use `html.escape()` on ANY user-controlled variable before inserting it into an HTML f-string or template used with `unsafe_allow_html=True`.
