## 2026-01-21 - [Streamlit Rerun Optimization]
**Learning:** Streamlit re-executes the entire script top-to-bottom on every interaction. Large constant data structures defined in the main script are re-allocated/parsed every time, which can add up.
**Action:** Move static data to a separate module. Python caches module imports, so the data is loaded once into memory and reused, avoiding re-allocation overhead.
