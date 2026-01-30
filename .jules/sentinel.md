## 2026-01-30 - [Manual HTML Construction in Streamlit]
**Vulnerability:** Extensive use of `unsafe_allow_html=True` with manual string interpolation (f-strings) for UI components.
**Learning:** The application bypasses Streamlit's native component safety by manually building HTML for styling (cards, lists), making it highly susceptible to XSS via user inputs.
**Prevention:** Avoid manual HTML construction where possible; use `html.escape()` strictly on all interpolated variables if manual HTML is necessary.
