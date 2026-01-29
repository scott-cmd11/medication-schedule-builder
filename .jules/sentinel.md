## 2024-10-27 - Streamlit Unsafe HTML Injection
**Vulnerability:** User input (medication names, units) was directly interpolated into `st.markdown(..., unsafe_allow_html=True)` strings, allowing stored XSS.
**Learning:** Streamlit's `unsafe_allow_html=True` is a powerful but dangerous feature. When rendering custom components with dynamic data, all variables must be explicitly sanitized.
**Prevention:** Use `html.escape()` for all dynamic data injected into HTML strings. Alias `import html as html_lib` if the local variable `html` shadows the module.
