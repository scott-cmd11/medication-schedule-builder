## 2025-05-23 - Streamlit XSS via st.markdown
**Vulnerability:** XSS in `st.markdown(..., unsafe_allow_html=True)` when interpolating user input directly.
**Learning:** Streamlit's `unsafe_allow_html=True` is powerful but dangerous. Standard Python f-strings don't escape HTML. Local variable names like `html` are common in generators, so `import html` can conflict.
**Prevention:** Always use `html.escape()` on any variable interpolated into HTML strings in Streamlit. Use `import html as html_lib` to avoid shadowing local `html` variables.
