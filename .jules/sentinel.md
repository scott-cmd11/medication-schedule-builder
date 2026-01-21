## 2024-05-22 - Cross-Site Scripting (XSS) in Streamlit UI
**Vulnerability:** User-supplied medication names were directly interpolated into HTML strings used in `st.markdown(unsafe_allow_html=True)`.
**Learning:** Streamlit's `unsafe_allow_html=True` is a powerful feature but requires manual sanitization of all dynamic content. It does not auto-escape variables in f-strings.
**Prevention:** Always use `html.escape()` when inserting variable data into HTML strings, especially when `unsafe_allow_html=True` is enabled.
