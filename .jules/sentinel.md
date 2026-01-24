## 2024-05-23 - Streamlit XSS Vulnerability
**Vulnerability:** Persistent Cross-Site Scripting (XSS) via `st.markdown(..., unsafe_allow_html=True)`. User input (medication names) was directly interpolated into HTML strings.
**Learning:** Streamlit applications often use `unsafe_allow_html=True` for custom styling, but this bypasses Streamlit's built-in escaping. Any user input flowing into these blocks must be manually escaped.
**Prevention:** Always use `html.escape()` when injecting dynamic data into HTML strings, even if the data seems trusted (defense in depth).
