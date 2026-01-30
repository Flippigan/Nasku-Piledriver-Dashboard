# Issues

## Issue 1: httpx.ReadError on Supabase connection

**Status:** Resolved (2026-01-30)
**Date:** 2026-01-30
**Severity:** Critical (dashboard not loading)

### Error

```
httpx.ReadError: [Errno 35] Resource temporarily unavailable
```

### Root Cause

Transient network error. Errno 35 (EAGAIN) on macOS indicates the resource is temporarily unavailable during non-blocking I/O. The connection works when retried.

### Solution Applied

Added graceful error handling in `src/ui/state.py:16-33` that:
1. Tests the Supabase connection by calling `get_project()` after client creation
2. If connection fails, displays a warning and falls back to demo mode
3. Prevents the app from crashing on transient network issues

```python
if supabase_url and supabase_key:
    try:
        from src.data.supabase_repo import SupabaseRepository
        repo = SupabaseRepository()
        repo.get_project()  # Test connection
        st.session_state.repository = repo
        st.session_state.using_demo_mode = False
    except Exception as e:
        st.warning(f"Could not connect to Supabase: {e}. Using demo mode.")
        from src.data.memory_repo import MemoryRepository
        st.session_state.repository = MemoryRepository()
        st.session_state.using_demo_mode = True
```

---

## Issue 2: HTML cards rendering as raw text

**Status:** Resolved (2026-01-30)
**Date:** 2026-01-30
**Severity:** Critical (dashboard unusable)

### Symptoms

- Dashboard cards displayed raw CSS/HTML as text instead of rendering
- HTML comments like `<!-- Inverter Name -->` visible in UI
- Style properties shown as plain text: `font-family: 'SF Mono'...`
- "View Details" buttons rendered correctly (Streamlit native)

### Root Cause

`st.markdown(html, unsafe_allow_html=True)` was not properly rendering complex nested HTML in Streamlit 1.53.1. The markdown parser was escaping or corrupting the HTML content before rendering.

### Solution Applied

Changed from `st.markdown()` to `st.html()` in `src/ui/dashboard.py`:

1. Card rendering (line 191): `st.markdown(card_html, unsafe_allow_html=True)` → `st.html(card_html)`
2. CSS injection (line 204): `st.markdown(..., unsafe_allow_html=True)` → `st.html(...)`
3. Grid container open/close (lines 312, 333): Same change

`st.html()` renders HTML directly without markdown processing, avoiding the escaping issue.

### Environment

- Streamlit 1.53.1
- Python 3.14.1
- macOS

---

## Issue 3: Slow loading when clicking "View Details"

**Status:** Resolved (2026-01-30)
**Date:** 2026-01-30
**Severity:** Medium (performance issue)

### Symptoms

- Clicking "View Details" button on an inverter card causes slow loading
- UI becomes unresponsive during the load
- Same slowness when clicking "Back to Dashboard" from details view

### Root Cause

N+1 query problem in `src/ui/dashboard.py`. For every inverter, the dashboard made 3 separate repository calls:
1. `get_piles_for_inverter()`
2. `get_workflow_steps()`
3. `get_alerts_for_inverter()`

With 36 inverters, this resulted in 109 database round trips on every navigation. Both directions were affected because `st.rerun()` always re-rendered the entire dashboard.

### Solution Applied

Added `@st.cache_data(ttl=5)` caching to dashboard card data collection in `src/ui/dashboard.py`:

1. Created `_get_all_cards_data()` cached function (lines 231-244) that fetches all card data once
2. Added `clear_dashboard_cache()` helper function (lines 261-263) for cache invalidation
3. Updated `src/ui/import_panel.py` to clear cache after imports and resets
4. Updated Reset button in dashboard to clear cache

The 5-second TTL balances data freshness with performance, and the `_repo` parameter prefix tells Streamlit not to hash the repository object.

### Result

After first load, navigation to/from details views uses cached data, eliminating the 109-query overhead.

---

## Issue 4: Slow initial dashboard load when cache is cold

**Status:** Resolved (2026-01-30)
**Date:** 2026-01-30
**Severity:** Medium (performance issue)

### Symptoms

- When `_get_all_cards_data()` cache is empty (cold), dashboard loading takes a long time
- Streamlit shows "Running _get_all_cards_data(...)." spinner during this time
- Occurs in these scenarios:
  1. **First dashboard load** - when app starts or page refreshes
  2. **Returning from details view** - clicking "Back to Dashboard" from an inverter card
  3. After cache TTL expires (5s) or after explicit cache clear (import/reset)

### Root Cause

Sequential data fetching in `_get_all_cards_data()`. For each inverter, the code made 4 sequential repository calls:
1. `get_inverter()`
2. `get_piles_for_inverter()`
3. `get_workflow_steps()`
4. `get_alerts_for_inverter()`

With 36 inverters, this resulted in 144 sequential HTTP requests to Supabase when the cache was cold.

### Solution Applied

Used `concurrent.futures.ThreadPoolExecutor` to parallelize the per-inverter data fetching in `src/ui/dashboard.py`, with:

1. **Reduced worker count to 4** - Stays well under HTTP/2 stream limits (servers typically allow 100-250 concurrent streams). With 4 workers × 4 queries each = 16 concurrent streams max.

2. **Sequential fallback** - If HTTP/2 connection errors occur (`RemoteProtocolError`), falls back to sequential fetching:

```python
def _fetch_cards_parallel(_repo, inverter_ids):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_fetch_card_data_for_inverter, inv_id, _repo): inv_id
            for inv_id in inverter_ids
        }
        for future in as_completed(futures):
            card = future.result()
            if card:
                cards.append(card)
    return cards

@st.cache_data(ttl=5)
def _get_all_cards_data(_repo, project_id, inverter_ids):
    try:
        cards = _fetch_cards_parallel(_repo, inverter_ids)
    except Exception:
        # HTTP/2 connection errors - fall back to sequential
        cards = _fetch_cards_sequential(_repo, inverter_ids)
    return sorted(cards, key=lambda x: x["name"])
```

### Result

Cold-cache dashboard load is faster with parallel fetching, and robust against HTTP/2 connection limit errors via sequential fallback.

---

## Issue 5: HTTP/2 RemoteProtocolError on parallel fetching

**Status:** Resolved (2026-01-30)
**Date:** 2026-01-30
**Severity:** Critical (dashboard crash)

### Error

```
httpx.RemoteProtocolError: <ConnectionTerminated error_code:1, last_stream_id:369, additional_data:None>
```

### Symptoms

- Dashboard crashes when returning from details view to home screen
- Error occurs in `_get_all_cards_data()` during parallel data fetching
- `last_stream_id:369` indicates HTTP/2 stream limit was exceeded

### Root Cause

The initial parallel fetching implementation (Issue 4 fix) used 10 worker threads. With each worker making 4 HTTP requests per inverter, and the Supabase client reusing a single HTTP/2 connection, we exceeded the server's concurrent stream limit.

HTTP/2 servers typically allow 100-250 concurrent streams per connection. With 10 workers × multiple inverters, we hit ~369 streams before the server terminated the connection.

### Solution Applied

1. **Reduced `max_workers` from 10 to 4** - Keeps concurrent streams well under HTTP/2 limits (4 workers × 4 queries = 16 max concurrent)

2. **Added exception handling with sequential fallback** - If parallel fetching fails due to connection errors, automatically falls back to sequential fetching:

```python
try:
    cards = _fetch_cards_parallel(_repo, inverter_ids)
except Exception:
    cards = _fetch_cards_sequential(_repo, inverter_ids)
```

### Result

Dashboard reliably loads even under HTTP/2 connection pressure, with graceful degradation to sequential fetching if needed.
