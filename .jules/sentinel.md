## 2025-02-18 - Stored XSS in Streamlit Markdown
**Vulnerability:** User input (medication names) was interpolated directly into `st.markdown` calls with `unsafe_allow_html=True`, allowing arbitrary HTML/JS execution.
**Learning:** Streamlit apps often use `unsafe_allow_html=True` for custom styling, creating invisible XSS sinks if developers assume `st.*` methods are always safe.
**Prevention:** Wrappers around `st.markdown` should enforce sanitization, or `html.escape()` must be used on every dynamic variable injected into HTML strings.
