# Windows Runtime Error: Streamlit Package Metadata Not Found

## Error Summary

| Field | Value |
|-------|-------|
| **When** | Running `InverterTracker.exe` on Windows |
| **Build** | v0.1.1-test (PyInstaller bundle) |
| **Status** | Diagnosed - fix pending |

## Full Traceback

```
Unhandled exception in script
Failed to execute script 'launcher' due to unhandled exception: No package metadata was found for streamlit

Traceback (most recent call last):
  File "importlib\metadata\__init__.py", line 563, in from_name
StopIteration

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "launcher.py", line 107, in <module>
  File "launcher.py", line 69, in main
  File "pyimod02_importers.py", line 457, in exec_module
  File "streamlit\__init__.py", line 64, in <module>
    from streamlit.version import STREAMLIT_VERSION_STRING as _STREAMLIT_VERSION_STRING
  File "pyimod02_importers.py", line 457, in exec_module
  File "streamlit\version.py", line 18, in <module>
    STREAMLIT_VERSION_STRING: Final[str] = _version("streamlit")
  File "importlib\metadata\__init__.py", line 1009, in version
  File "importlib\metadata\__init__.py", line 982, in distribution
  File "importlib\metadata\__init__.py", line 565, in from_name
importlib.metadata.PackageNotFoundError: No package metadata was found for streamlit
```

---

## Root Cause (Confirmed)

**PyInstaller does not collect package metadata (`.dist-info` directories) by default.**

When Streamlit imports, it calls `importlib.metadata.version("streamlit")` in `streamlit/version.py` to determine its version string. Without the metadata present in the frozen bundle, this lookup fails with `PackageNotFoundError`.

This is a well-documented issue. The pattern `__version__ = importlib.metadata.version("package")` is recommended by setuptools_scm and many modern packages, but PyInstaller's default behavior does not accommodate it.

---

## Recommended Fix

### Fix 1: Add `copy_metadata()` to Spec File

Use PyInstaller's `copy_metadata()` utility function to explicitly include Streamlit's metadata in the bundle.

**Changes to `build_windows.spec`:**

```python
# -*- mode: python ; coding: utf-8 -*-
# Windows build spec for Inverter Tracker

import streamlit
import os
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata  # <-- Add this import

streamlit_path = os.path.dirname(streamlit.__file__)

# Collect metadata for packages that use importlib.metadata
datas = copy_metadata('streamlit')  # <-- Add this line

a = Analysis(
    ['src/launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        (streamlit_path, 'streamlit'),
        ('src', 'src'),
        ('.env', '.'),
    ] + datas,  # <-- Append the metadata here
    # ... rest of Analysis unchanged
)
```

**Why this fix:**
- Minimal change - only requires importing one function and appending to datas
- Directly addresses the root cause - the error is specifically about missing metadata
- Well-tested - this is the documented PyInstaller solution

---

## Alternative Fixes

### Fix 2: Use `collect_all()` for Comprehensive Collection

If Fix 1 doesn't fully resolve the issue, use `collect_all()` which gathers submodules, data files, binaries, AND metadata in one call.

```python
from PyInstaller.utils.hooks import collect_all

st_datas, st_binaries, st_hiddenimports = collect_all('streamlit')

a = Analysis(
    ['src/launcher.py'],
    binaries=st_binaries,
    datas=[
        ('src', 'src'),
        ('.env', '.'),
    ] + st_datas,
    hiddenimports=[...] + st_hiddenimports,
)
```

**Pros:** Most comprehensive
**Cons:** May increase bundle size

### Fix 3: Create a Custom Hook File

Create `hooks/hook-streamlit.py`:

```python
from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

datas = copy_metadata('streamlit')
datas += collect_data_files('streamlit')
hiddenimports = collect_submodules('streamlit')
```

Then add `hookspath=['./hooks']` to the spec file.

---

## Other Dependencies at Risk

These packages may also use `importlib.metadata` and could cause similar errors:

| Package | Risk Level | Notes |
|---------|------------|-------|
| **pydantic** | Medium | Known PyInstaller issues; may need `copy_metadata('pydantic')` |
| **altair** | Low | Has a contributed hook in pyinstaller-hooks-contrib |
| **pandas** | Low | Typically doesn't use importlib.metadata for version |
| **supabase** | Unknown | May have transitive dependencies that use metadata |

**Defensive approach** - add metadata for multiple packages:

```python
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += copy_metadata('streamlit')
datas += copy_metadata('pydantic')
datas += copy_metadata('altair')
```

---

## Additional Caveats

1. **Console window**: `console=False` in the EXE configuration has been reported to cause issues with Streamlit. Try `console=True` for debugging if issues persist.

2. **Static files**: Streamlit requires its `static/` directory at runtime. Verify files are present in the bundle.

3. **Altair schemas**: If using Altair charts, may need to explicitly include schema files.

4. **PyInstaller version**: Ensure pyinstaller>=6.0.0. Older versions had more metadata issues.

---

## Files Involved

- `src/launcher.py:69` - calls `import streamlit.web.cli`
- `streamlit/version.py:18` - calls `_version("streamlit")`
- `build_windows.spec` - PyInstaller configuration

---

## References

- [PyInstaller Hooks Documentation - copy_metadata](https://pyinstaller.org/en/stable/hooks.html)
- [PyInstaller Discussion #6033 - importlib.metadata.PackageNotFoundError](https://github.com/orgs/pyinstaller/discussions/6033)
- [Streamlit Forum - Converting Streamlit into executable file](https://discuss.streamlit.io/t/converting-streamlit-into-executable-file/65451)
