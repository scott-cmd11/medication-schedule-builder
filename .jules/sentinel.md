# Sentinel Journal

## 2025-02-20 - Stored XSS in Medication List
**Vulnerability:** Stored Cross-Site Scripting (XSS) vulnerability in `app.py`. User-provided medication names (via manual entry) were interpolated directly into HTML strings rendered by `st.markdown(..., unsafe_allow_html=True)` without sanitization.
**Learning:** Streamlit's `unsafe_allow_html=True` is a common pitfall. It essentially disables Streamlit's built-in XSS protection for that component. When building custom UI components with HTML strings, developer vigilance is the only defense.
**Prevention:** Always use `html.escape()` on any variable derived from user input or external sources before embedding it in an HTML string. Prefer native Streamlit components (`st.container`, `st.metric`, etc.) over custom HTML where possible.
