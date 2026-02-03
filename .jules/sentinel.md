## 2025-02-03 - [Stored XSS in Streamlit Custom Components]
**Vulnerability:** Stored Cross-Site Scripting (XSS) via manual medication entry and API results interpolated into `st.markdown(..., unsafe_allow_html=True)`.
**Learning:** The application heavily relies on f-string interpolation for custom HTML components (Cards, Lists, Buttons) to bypass Streamlit's styling limitations. This creates widespread XSS risks because Streamlit does not auto-escape variables inside `unsafe_allow_html=True` blocks.
**Prevention:** Always wrap dynamic variables in `html.escape()` before interpolating them into HTML strings intended for `st.markdown`. Use `import html as html_lib` to avoid variable shadowing.
