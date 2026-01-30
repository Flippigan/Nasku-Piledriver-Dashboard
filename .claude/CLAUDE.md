# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app (demo mode if no .env configured)
streamlit run src/app.py

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_progress.py -v

# Run tests with coverage
pytest tests/ --cov=src

# Build standalone executable
./scripts/build.sh
```

## Architecture

This is a Streamlit dashboard for tracking pile installation progress across solar site inverters. Python 3.11+ required.

**Layered structure:**
- `src/ui/` - Streamlit components (dashboard grid, expanded card view, import panel)
- `src/services/` - Business logic (progress/ETA calculations, alerts, import orchestration)
- `src/data/` - Repository pattern with abstract interface and two implementations
- `src/import_/` - CSV parsing for Drivelog and Nasku formats

**Repository pattern:** Abstract `Repository` class in `repository.py` with:
- `SupabaseRepository` - Production PostgreSQL backend
- `MemoryRepository` - Demo mode with sample data (auto-enabled when no Supabase credentials)

**Key models (Pydantic v2):**
- `Project` - Settings like pile rate and scan thresholds
- `Inverter` - Total piles, milestone thresholds
- `Pile` - UPN, hammering status/flag, drive times. Has computed `is_installed` property (COMPLETED + GOOD)
- `WorkflowStep` - 11-step fixed workflow with due dates and assignments

**Session state:** Managed in `src/ui/state.py`. Repository instance stored in `st.session_state["repository"]`.

**CSV imports:** Drivelog creates piles, Nasku updates existing piles with drive times. Both use pandas for parsing.

## Database

Schema in `scripts/setup_database.sql`. Tables: projects, inverters, piles, workflow_steps, alerts.

Environment variables (from `.env`):
- `SUPABASE_URL` - Project URL
- `SUPABASE_KEY` - anon public key
