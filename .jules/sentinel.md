## 2026-02-01 - Streamlit Unsafe HTML Injection
**Vulnerability:** Stored XSS in Streamlit application via `st.markdown(..., unsafe_allow_html=True)`. User input (medication names) was interpolated directly into HTML strings without sanitization.
**Learning:** Streamlit's `unsafe_allow_html=True` is a powerful but dangerous feature. Developers often assume internal or "low-risk" apps don't need strict sanitization, but any user input reflected in the DOM is a vector.
**Prevention:** Always wrap variables in `html.escape()` when constructing HTML strings manually for `st.markdown`. Better yet, avoid `unsafe_allow_html=True` if possible, or use a templating engine with auto-escaping (like Jinja2) even for small fragments.
