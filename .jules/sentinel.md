## 2024-05-23 - Stored XSS in Streamlit Markdown
**Vulnerability:** User-controlled input (medication names) was being interpolated directly into `st.markdown(..., unsafe_allow_html=True)` strings, allowing for Stored XSS attacks.
**Learning:** Streamlit's `unsafe_allow_html=True` is often necessary for custom styling but completely bypasses Streamlit's default escaping. A local variable named `html` was used as a string accumulator, which would shadow the standard library `html` module if imported directly.
**Prevention:** Always alias the `html` module as `html_lib` (or similar) when importing in this project to avoid name collisions. Explicitly wrap ALL user inputs in `html_lib.escape()` before interpolating them into HTML strings used with `unsafe_allow_html=True`.
