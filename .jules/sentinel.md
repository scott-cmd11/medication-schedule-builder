## 2024-05-22 - Streamlit XSS via st.markdown
**Vulnerability:** Unsanitized user input injected into `st.markdown(..., unsafe_allow_html=True)` strings.
**Learning:** Streamlit's `unsafe_allow_html=True` is a common pattern for custom UI in this app, making XSS a systemic risk.
**Prevention:** Always wrap interpolated variables with `html.escape()`.
