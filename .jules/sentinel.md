
## 2026-01-19 - Stored XSS in Streamlit Markdown
**Vulnerability:** Found multiple Stored XSS vulnerabilities where user input (medication names, units) was directly interpolated into HTML strings used with `st.markdown(..., unsafe_allow_html=True)`.
**Learning:** Streamlit's `unsafe_allow_html=True` is powerful but dangerous. It does not auto-escape input. When building custom UI components (like cards or lists) with HTML, any dynamic data must be treated as untrusted.
**Prevention:** Always use `html.escape()` on ANY variable interpolated into an HTML string passed to `st.markdown`.
