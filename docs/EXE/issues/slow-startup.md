# Issue: Windows EXE Takes 15+ Minutes to Start

## Summary

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Component** | Windows executable (PyInstaller bundle) |
| **Build** | v0.1.2-test |
| **Status** | Open - Investigation complete, awaiting diagnostic build |
| **Last Updated** | 2026-01-31 |

## Problem Description

After launching `InverterTracker.exe` on Windows, the application takes an excessively long time to start (15+ minutes observed) with no indication of progress to the user. It is unclear if the app is working at all.

## Expected Behavior

The application should start within a reasonable time (seconds, not minutes). Streamlit apps typically launch in 2-5 seconds on modern hardware.

## Observed Behavior

- User double-clicks `InverterTracker.exe`
- No window appears
- Task Manager may or may not show the process
- After 15+ minutes, still no visible progress
- Unclear if app will ever start or has silently failed

## Environment

- OS: Windows (version TBD)
- Build: PyInstaller-bundled executable
- Streamlit version: >=1.31.0
- Python version: 3.11

---

## Investigation Findings (2026-01-31)

### Code Analysis Summary

Reviewed the following files:
- `src/launcher.py` - Entry point (107 lines)
- `build_windows.spec` - PyInstaller config (82 lines)
- `src/app.py` - Streamlit app (44 lines)
- `src/ui/state.py` - Session state management
- `src/ui/dashboard.py` - Main dashboard view

### Root Causes Identified

| # | Root Cause | Evidence | Severity |
|---|-----------|----------|----------|
| **1** | **Silent failures - `console=False`** | `build_windows.spec:75` hides all output | **Critical** |
| **2** | **PyInstaller single-file extraction** | `runtime_tmpdir=None` + `--onefile` extracts ~200-400MB to temp every launch | **High** |
| **3** | **Heavy import chain** | `import streamlit.web.cli` at `launcher.py:69` loads entire framework before any UI | **High** |
| **4** | **No user feedback** | No splash screen, no progress indicator | **Medium** |
| **5** | **30s server timeout** | `wait_for_server(port, timeout=30)` at `launcher.py:20` may timeout silently | **Medium** |

### Data Flow Analysis

```
User clicks EXE
    ↓
PyInstaller extracts to temp (SLOW - hundreds of MB, AV scans)
    ↓
launcher.py main() runs
    ↓
import streamlit.web.cli (SLOW - heavy import chain)
    ↓
Thread spawns stcli.main()
    ↓
wait_for_server() polls for 30 seconds
    ↓
If server doesn't bind → silent exit (no window, no error visible)
```

### Key Code Observations

**launcher.py architecture:**
```python
# Line 67-77: Frozen app path
if getattr(sys, "frozen", False):
    import streamlit.web.cli as stcli  # <-- Heavy import, blocks here

    def run_streamlit():
        sys.argv = ["streamlit", "run", str(app_path), ...]
        stcli.main()

    server_thread = threading.Thread(target=run_streamlit, daemon=True)
    server_thread.start()
```

**Problems:**
1. `import streamlit.web.cli` happens in main thread before any feedback
2. Entire framework (pandas, altair, pyarrow) loads during this import
3. No timing instrumentation exists
4. `console=False` means zero visibility into what's happening

**build_windows.spec configuration:**
```python
# Line 75 - Critical issue
console=False,  # Hide console window for end users

# Line 74 - May cause extraction overhead
runtime_tmpdir=None,  # Extracts to system temp
```

### Hypotheses (Ranked by Likelihood)

#### Hypothesis 1: Extraction + Import Chain = 15+ Minutes (Most Likely)

The combination of:
- PyInstaller single-file extraction (~1-5 min depending on disk/AV)
- Heavy Streamlit/pandas/altair import chain (~30s-2min)
- Windows Defender scanning extracted temp files (~variable)

These combine to create the 15+ minute wait.

#### Hypothesis 2: Server Never Starts (Silent Failure)

The Streamlit server fails due to a hidden exception (since `console=False`), the 30-second `wait_for_server` timeout occurs, but the error message at `launcher.py:102` is never shown because there's no console.

#### Hypothesis 3: AV Scanning Temp Directory

Windows Defender scans the extracted PyInstaller temp files aggressively, causing massive delays before Python code even begins executing.

### Related Issues

- `docs/EXE/windows-runtime-error.md` - Streamlit metadata error (fixed with `copy_metadata`)
- `docs/EXE/issues/no-loading-indicator.md` - Proposes tkinter splash screen

---

## Potential Root Causes

1. **PyInstaller extraction overhead** - Single-file EXE extracts to temp directory on each launch
2. **Streamlit server initialization** - May be blocking on network/port binding
3. **Import chain** - Heavy dependencies (pandas, altair, supabase) loading sequentially
4. **Antivirus scanning** - Windows Defender scanning extracted files
5. **Missing dependencies** - Silent failures during import causing hangs
6. **Browser launch blocking** - Waiting for browser that never opens

## Files Involved

- `src/launcher.py` - Entry point that spawns Streamlit
- `build_windows.spec` - PyInstaller configuration
- `src/app.py` - Main Streamlit application

## Investigation Areas

### Completed
- [x] Review launcher.py entry point architecture
- [x] Review build_windows.spec configuration
- [x] Analyze import chain and dependencies
- [x] Identify silent failure points
- [x] Document root cause hypotheses

### Next Steps (Diagnostic Build Required)
- [ ] Enable `console=True` in spec to see startup logs
- [ ] Add timing instrumentation to launcher.py (see template below)
- [ ] Build debug EXE and run on Windows
- [ ] Capture timing data to confirm which phase is slow
- [ ] Profile import times for heavy dependencies
- [ ] Check if Streamlit server binds to port successfully
- [ ] Test with `--onedir` instead of `--onefile` mode
- [ ] Check Windows Event Viewer for errors

---

## Recommended Fix Strategy

### Phase 1: Diagnostic Build (Required First)

Before implementing fixes, we need timing data to confirm which phase is slow.

**1. Enable console in build_windows.spec:**
```python
# Change line 75 from:
console=False,
# To:
console=True,  # DEBUG: Show console for startup diagnostics
```

**2. Add timing instrumentation to launcher.py:**
```python
"""Windows launcher - starts Streamlit server and opens browser."""

import time
_start = time.time()
def _log(msg):
    print(f"[{time.time() - _start:7.2f}s] {msg}", flush=True)

_log("launcher.py started")

import os
import sys
import socket
import subprocess
import threading
import webbrowser
from pathlib import Path

_log("stdlib imports complete")

# ... rest of imports ...

def main():
    _log("main() entered")

    from dotenv import load_dotenv
    _log("dotenv imported")

    # ... existing code ...

    _log("About to import streamlit.web.cli")
    import streamlit.web.cli as stcli
    _log("streamlit.web.cli imported")

    # ... in wait_for_server loop ...
    # Add: _log(f"Waiting for server... attempt {attempt}")
```

**3. Build and run on Windows, capture console output**

### Phase 2: Implement Fixes Based on Data

Once timing data confirms the bottleneck:

| If Slow Phase Is... | Recommended Fix |
|---------------------|-----------------|
| PyInstaller extraction | Switch to `--onedir` mode, or use `runtime_tmpdir` pointing to excluded folder |
| Streamlit import | Add splash screen before import (see `no-loading-indicator.md`) |
| Server startup | Increase timeout, add retry logic, check port conflicts |
| AV scanning | Document AV exclusion for users, sign the EXE |

### Phase 3: Long-term Solutions

1. **Splash screen** - Show tkinter window immediately (see `no-loading-indicator.md`)
2. **--onedir mode** - Avoid extraction overhead (larger folder, but faster startup)
3. **Lazy imports** - Defer heavy imports until after splash is shown
4. **Code signing** - Reduces AV scanning time on Windows

---

## Debugging Prompt

Copy and paste this prompt to continue the debugging session:

```
/systematic-debugging

Context: Windows EXE startup performance issue - PHASE 3 (Diagnostic Build)

Bug: After launching InverterTracker.exe on Windows, the application takes 15+ minutes to show any UI.

Documentation: docs/EXE/issues/slow-startup.md

Investigation Status: Root cause analysis complete. Need to implement diagnostic build.

Next action: Implement the timing instrumentation described in "Recommended Fix Strategy > Phase 1" in this document:
1. Set console=True in build_windows.spec
2. Add timing instrumentation to launcher.py
3. Build debug EXE
4. Run on Windows and capture timing output

Key files to modify:
- src/launcher.py (add timing logs)
- build_windows.spec (enable console)

Root causes identified (need timing data to confirm which is primary):
1. console=False hiding all errors (Critical)
2. PyInstaller single-file extraction overhead (High)
3. Heavy streamlit import chain (High)
4. No user feedback during startup (Medium)
5. 30s server timeout may fail silently (Medium)
```
