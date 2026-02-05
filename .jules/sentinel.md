## 2024-05-23 - [Stored XSS via Streamlit Markdown]
**Vulnerability:** User input (medication name) was interpolated directly into HTML strings passed to `st.markdown(..., unsafe_allow_html=True)`, allowing arbitrary JavaScript execution.
**Learning:** Streamlit's `unsafe_allow_html=True` is a dangerous sink. Even when inputs are expected to be benign (like numeric dose values), they should be treated as untrusted and escaped.
**Prevention:** Always use `html.escape()` on ANY dynamic content interpolated into HTML, including numeric values (defense in depth). Use dedicated security regression tests mocking the Streamlit environment.
