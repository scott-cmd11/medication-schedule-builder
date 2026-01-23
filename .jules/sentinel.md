## 2024-05-23 - XSS and Module Shadowing
**Vulnerability:** Reflected Cross-Site Scripting (XSS) in medication name display due to unsafe HTML interpolation in `st.markdown`.
**Learning:** When fixing XSS by importing `html` module, I discovered that local variables named `html` (used for accumulating HTML strings) shadowed the imported module, causing `AttributeError: 'str' object has no attribute 'escape'`.
**Prevention:** Always use an alias (e.g., `import html as html_lib`) when importing modules that share names with common variable names, or avoid using module names as variable names.
