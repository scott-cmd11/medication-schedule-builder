## 2024-05-23 - Stored XSS in Streamlit
**Vulnerability:** Identified Stored XSS where user input (medication names) was stored in `st.session_state` and rendered unsanitized via `st.markdown(..., unsafe_allow_html=True)`.
**Learning:** Streamlit's `unsafe_allow_html=True` is dangerous when combined with f-strings interpolating session state variables. Even in a simple Python app, manual HTML construction requires explicit escaping.
**Prevention:** Always use `html.escape()` when interpolating any variable into an HTML string destined for `st.markdown` or similar functions. Cast variables to `str()` first to handle non-string types gracefully.
