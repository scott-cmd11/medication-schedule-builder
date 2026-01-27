## 2025-02-18 - XSS in Streamlit Markdown
**Vulnerability:** User inputs (medication name, dose, etc.) were directly interpolated into HTML strings passed to `st.markdown(..., unsafe_allow_html=True)`.
**Learning:** Streamlit does not automatically escape variables when using `unsafe_allow_html=True`, placing the burden of sanitization entirely on the developer. This is a common pitfall when building custom UI components in Streamlit.
**Prevention:** Always wrap dynamic variables with `html.escape()` before interpolating them into HTML strings in Streamlit applications.
