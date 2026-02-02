# Parallel Debugging Prompt for Windows Build Failure

Copy and paste this prompt into a new Claude session:

---

## Context

I'm trying to package a Streamlit Python app as a Windows .exe using PyInstaller and GitHub Actions. The build failed.

**Repository:** https://github.com/Flippigan/Nasku-Piledriver-Dashboard
**Branch:** `feature/windows-exe-build`
**Failed tag:** `v0.1.0-test`

**Key files:**
- `.github/workflows/build-windows.yml` - GitHub Actions workflow
- `build_windows.spec` - PyInstaller spec file
- `src/launcher.py` - Windows launcher entry point
- `requirements.txt` - Python dependencies

**Stack:**
- Python 3.11
- Streamlit
- Supabase client
- Pandas, Pydantic

## Your Task

1. First, fetch the GitHub Actions log from: https://github.com/Flippigan/Nasku-Piledriver-Dashboard/actions
2. Identify the specific error causing the build failure
3. Propose a fix with the exact file changes needed
4. If there are multiple potential issues, list them in order of likelihood

## Common PyInstaller + Streamlit Issues to Check

- Missing hidden imports (streamlit has many internal modules)
- Missing data files (streamlit static assets)
- Hook configuration issues
- Dependency conflicts on Windows
- Path issues with bundled files

Do not make changes - just diagnose and propose fixes.
