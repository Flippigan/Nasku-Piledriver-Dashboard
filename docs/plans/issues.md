# Implementation Issues

## Issue 1: ModuleNotFoundError for 'src' module

**Date:** 2026-01-29

**Error:**
```
ModuleNotFoundError: No module named 'src'

File "/Users/finnjohnson/Documents/Boldt Projects/Inverter Tracker Dashboard/src/app.py", line 6, in <module>
    from src.ui.state import init_session_state
```

**Context:** Occurs when running the Streamlit app directly.

**Status:** ✅ Resolved (2026-01-29)

**Root Cause:** When running `streamlit run src/app.py`, Python's working directory is the project root, but `src/` is not on `sys.path`. The imports use absolute paths like `from src.ui.state import ...` which require the project root to be on `sys.path`.

**Solution Applied:** Added path manipulation at the top of `src/app.py`:
```python
import sys
from pathlib import Path

# Add project root to path for 'src' package imports
# Works for both local development and PyInstaller builds
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
```

This approach was chosen because:
1. No external setup required (unlike PYTHONPATH or editable install)
2. Works for both local development and PyInstaller packaging
3. Uses `Path(__file__)` which resolves correctly in bundled apps
