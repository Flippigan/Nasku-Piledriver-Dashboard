# Issue: No Loading Indicator When Windows EXE Starts

## Summary

| Field | Value |
|-------|-------|
| **Severity** | Medium |
| **Component** | Windows executable (PyInstaller bundle) |
| **Build** | v0.1.2-test |
| **Status** | Open - Design needed |
| **Blocked by** | slow-startup.md (fix performance first) |

## Problem Description

When launching `InverterTracker.exe`, there is no visual feedback to indicate the application is loading. Users have no way to know if:

- The app is starting up normally
- The app has crashed silently
- They need to continue waiting
- They should try launching again

This creates a poor user experience and causes confusion, especially combined with the slow startup time.

## Expected Behavior

Immediate visual feedback when the application is launched:
- A splash screen, loading dialog, or window appears within 1-2 seconds
- Progress indication shows the app is working
- User knows to wait rather than re-launching

## Observed Behavior

- User double-clicks EXE
- Nothing visible happens
- No taskbar icon
- No system tray icon
- No splash screen
- User assumes app is broken and may launch multiple instances

## Technical Constraints

1. **PyInstaller extraction** - Happens before any Python code runs
2. **Streamlit architecture** - Server must start before UI appears
3. **Single-file EXE** - Cannot show UI during extraction phase
4. **console=False** - No terminal output visible

## Proposed Solutions

### Option A: Splash Screen (Recommended)

Create a lightweight splash window using tkinter (bundled with Python) that:
1. Appears immediately when launcher.py starts
2. Shows "Loading Inverter Tracker..." with a spinner
3. Closes when Streamlit server is ready

```python
# In launcher.py
import threading
from tkinter import Tk, Label

def show_splash():
    splash = Tk()
    splash.title("Loading...")
    splash.geometry("300x100")
    Label(splash, text="Loading Inverter Tracker...", font=("Arial", 14)).pack(expand=True)
    splash.mainloop()

# Start splash in background thread
splash_thread = threading.Thread(target=show_splash, daemon=True)
splash_thread.start()

# Continue with Streamlit launch...
```

### Option B: System Tray Icon

Use `pystray` to show a system tray icon immediately with tooltip "Starting...".

### Option C: Console Window (Debug Mode)

Temporarily set `console=True` in build_windows.spec to show startup logs. Not ideal for end users but useful for debugging.

### Option D: Progress File

Write progress to a temp file that a separate lightweight monitor process displays.

## Files Involved

- `src/launcher.py` - Entry point, would contain splash logic
- `build_windows.spec` - May need to add tkinter to hiddenimports

## Dependencies

- `tkinter` - Built into Python, no additional install
- OR `pystray` - Would need to add to requirements.txt

---

## Debugging Prompt

Copy and paste this prompt to start a debugging/implementation session:

```
/systematic-debugging

Context: Windows EXE missing loading indicator

Bug: When launching InverterTracker.exe, there is no visual feedback. Users cannot tell if the app is loading, crashed, or if they should wait.

Documentation: docs/EXE/issues/no-loading-indicator.md

Key files:
- src/launcher.py (entry point - add splash here)
- build_windows.spec (may need tkinter in hiddenimports)

This is more of a missing feature than a bug. The goal is to add immediate visual feedback when the EXE launches.

Proposed solution: Add a tkinter splash screen in launcher.py that:
1. Appears immediately on launch
2. Shows "Loading..." message
3. Closes when Streamlit is ready or after timeout

Verify:
1. tkinter is available in PyInstaller bundle
2. Splash appears before heavy imports
3. Splash closes cleanly when app is ready
4. Threading doesn't block Streamlit startup
```
