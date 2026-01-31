## 2026-01-31 - [Health Canada API Caching]
**Learning:** External APIs like Health Canada's can be extremely slow (>50s) or unreliable. Without caching, this makes the app unusable for repeated searches.
**Action:** Always wrap external data fetching with `@st.cache_data`. Separate the raw data fetching (side effect) from the preprocessing/logic to maximize cacheability. Pre-process inputs (e.g. string cleaning) *before* calling the cached function to improve cache hit rates.
