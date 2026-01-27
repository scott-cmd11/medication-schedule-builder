
## 2026-01-27 - Inline Search vs Cached Function
**Learning:** Found `search_medications` was defined but unused, with search logic duplicated inline. The inline logic performed `.lower()` on every iteration (O(N) string allocations). Replacing it with the cached function using `@st.cache_data` reduced search time from ~0.2s to ~0s for repeated queries and simplified the code.
**Action:** Always check for existing unused utility functions before optimizing inline logic. Use `@st.cache_data` for compute-heavy UI elements like PDF generation.
