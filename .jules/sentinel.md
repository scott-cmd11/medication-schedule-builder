## 2026-01-17 - Stored XSS in Streamlit Custom Components
**Vulnerability:** Stored XSS via manual medication entry. User input (`med['name']`, `med['strength_value']`, etc.) was being directly interpolated into HTML strings and rendered with `st.markdown(..., unsafe_allow_html=True)`.
**Learning:** Streamlit apps often use `unsafe_allow_html=True` to bypass layout limitations. This creates XSS risks if any user input is displayed within these blocks.
**Prevention:** Always wrap variables interpolated into `st.markdown` HTML strings with `html.escape()`. Treat any data source (even internal databases if they accept user input) as untrusted when rendering raw HTML.
