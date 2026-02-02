## 2026-02-02 - Stored XSS in Streamlit Markdown
**Vulnerability:** Stored Cross-Site Scripting (XSS) via `st.markdown(..., unsafe_allow_html=True)` where medication names (user input or API data) were interpolated directly into HTML strings without sanitization.
**Learning:** In Streamlit apps using `unsafe_allow_html=True` for custom UI, every dynamic variable must be treated as hostile. Also, the variable name `html` is commonly used for string building, so `import html` must be aliased (e.g. `import html as html_lib`) to avoid shadowing.
**Prevention:** Wrap all interpolated variables in `html_lib.escape(str(var))` when building HTML strings for `st.markdown`.
