## 2024-05-23 - [Caching Network & Compute Bottlenecks]
**Learning:** In Streamlit apps, duplicated logic in the render loop (like inline search) combined with expensive re-computations (PDF generation) and network calls (API search) on every interaction significantly degrades performance. Caching these side-effect-free functions with `@st.cache_data` is the most impactful optimization.
**Action:** Always audit Streamlit render loops for expensive operations and move them to cached functions.
