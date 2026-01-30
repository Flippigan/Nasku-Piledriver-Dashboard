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

---

## Issue 2: Missing 'is_installed' column in Supabase schema

**Date:** 2026-01-29

**Error:**
```
Import failed: {'message': "Could not find the 'is_installed' column of 'piles' in the schema cache", 'code': 'PGRST204', 'hint': None, 'details': None}
```

**Context:** Occurs when importing a drivelog CSV with Supabase configured.

**Status:** ✅ Resolved (2026-01-29)

**Root Cause:**

The `Pile` model in `src/data/models.py:36-42` defines `is_installed` as a Pydantic `@computed_field`:

```python
@computed_field
@property
def is_installed(self) -> bool:
    return (
        self.hammering_status == "COMPLETED"
        and self.hammering_flag == "GOOD"
    )
```

Pydantic v2's `@computed_field` decorator **includes computed properties in serialization by default**. When `save_piles()` in `src/data/supabase_repo.py:87` calls `p.model_dump(mode="json")`, the output includes `is_installed: True/False`:

```python
def save_piles(self, piles: list[Pile]) -> list[Pile]:
    data = [p.model_dump(mode="json") for p in piles]  # includes is_installed!
    result = self.client.table("piles").insert(data).execute()
```

The `piles` table in Supabase (defined in `scripts/setup_database.sql:30-40`) does NOT have an `is_installed` column - by design, it's a computed/derived value. PostgREST rejects the insert with error `PGRST204` because the column doesn't exist.

**Data flow:**
```
CSV Import → Pile objects created → save_piles() → model_dump() includes is_installed
→ Supabase insert → PostgREST rejects unknown column → Error PGRST204
```

**Solution Applied:** Added `exclude={"is_installed"}` to `model_dump()` calls in `src/data/supabase_repo.py` for both `save_piles()` and `update_pile()` methods:

```python
# save_piles() - line 87
data = [p.model_dump(mode="json", exclude={"is_installed"}) for p in piles]

# update_pile() - line 92
data = pile.model_dump(mode="json", exclude={"is_installed"})
```

This prevents the computed `is_installed` field from being sent to Supabase while still allowing it to be used in the application logic.

---

## Issue 3: CSV column naming conventions mixed up between Drivelog and Nasku

**Date:** 2026-01-29

**Error:**
```
Missing required columns: name, processedAt, positioningTime, hammeringTime, hammeringStatus, hammeringFlag
```

**Context:** Occurs when importing CSV files - the wrong column validation is being applied.

**Status:** ✅ Resolved (2026-01-29) - Reset Project implemented

**Root Cause:** UI auto-selects import type based on application state, not user choice.

The import panel (`src/ui/import_panel.py:22-75`) has **no user-selectable import type**. The importer is chosen automatically based on whether a project exists:

| Project State | UI Shows | Validation Applied |
|---------------|----------|-------------------|
| No project exists | "Step 1: Import Drivelog" only (lines 22-48) | Drivelog columns |
| Project exists | "Import Nasku Progress Update" only (lines 50-75) | Nasku columns |

**There is no way for a user to override this selection.**

The two CSV formats have different column naming conventions:

**Drivelog columns** (defined in `src/import_/drivelog_importer.py:8`):
- `Inverter`, `UPN`, `Hammering_Status`, `Hammering_Flag`
- Uses Title_Snake_Case

**Nasku columns** (defined in `src/import_/nasku_importer.py:9-12`):
- `name`, `processedAt`, `positioningTime`, `hammeringTime`, `hammeringStatus`, `hammeringFlag`
- Uses camelCase

**Reproduction Scenario:**

1. User imports a Drivelog → project is created
2. User realizes they uploaded the wrong Drivelog file
3. User clicks "Import CSV" from dashboard (`src/ui/dashboard.py:117`)
4. Import panel now only shows Nasku import (because project exists)
5. User uploads their corrected Drivelog file anyway
6. Nasku validation is applied → fails with Nasku column names

**Data Flow Where Error Occurs:**

```
User uploads Drivelog.csv (has: Inverter, UPN, Hammering_Status, Hammering_Flag)
    ↓
import_panel.py sees project exists → routes to Nasku path (line 54-75)
    ↓
import_service.import_nasku() called (line 64)
    ↓
NaskuData.from_csv() → parse_nasku() → validate_required_columns()
    ↓
Validates against: name, processedAt, positioningTime, etc.
    ↓
MissingColumnsError with Nasku columns (none match Drivelog columns)
```

**Contributing Factors:**

1. **No import type selector** - The UI decides for the user based on app state
2. **"Reset Project" is unimplemented** (`src/ui/import_panel.py:83-84`) - Users cannot delete a project to re-import a Drivelog
3. **Button labeling mismatch** - Dashboard shows generic "Import CSV" button (`src/ui/dashboard.py:117`) but import panel forces Nasku-only when project exists
4. **No auto-detection** - The importers don't sniff column headers to determine file type

**Potential Solutions:**

1. Add import type selector (radio/dropdown) to let user choose Drivelog vs Nasku
2. Implement "Reset Project" functionality to allow re-importing Drivelog
3. Auto-detect file type by inspecting column headers before validation
4. Show clearer UI messaging about which file type is expected

**Solution Applied:** Implement "Reset Project" functionality

---

## Issue 3 Implementation Plan: Reset Project

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Allow users to delete all project data and re-import a fresh Drivelog CSV.

**Architecture:** Add `reset_all()` method to Repository abstract class, implement in both MemoryRepository (clear dicts) and SupabaseRepository (delete rows in FK order), wire up existing UI button.

**Tech Stack:** Python, Pydantic, Supabase PostgREST, Streamlit

**Progress:**
- Tasks 1-3 completed in commit `2c3fb7c` (2026-01-29)
- Tasks 4-5 pending

---

### Task 1: Add abstract method to Repository ✅

**Files:**
- Modify: `src/data/repository.py:79` (after `acknowledge_alert`)

**Step 1: Add the abstract method**

Add after line 79:

```python
    # Reset methods
    @abstractmethod
    def reset_all(self) -> None:
        """Delete all data (project, inverters, piles, workflow_steps, alerts)."""
        pass
```

**Step 2: Verify syntax**

Run: `python -c "from src.data.repository import Repository"`
Expected: No errors (abstract class loads)

**Step 3: Commit**

```bash
git add src/data/repository.py
git commit -m "feat(repo): add abstract reset_all method"
```

---

### Task 2: Implement reset_all in MemoryRepository ✅

**Files:**
- Modify: `src/data/memory_repo.py:161` (end of file)

**Step 1: Add the implementation**

Add after line 160:

```python
    # Reset methods
    def reset_all(self) -> None:
        self._project = None
        self._inverters.clear()
        self._piles.clear()
        self._workflow_steps.clear()
        self._alerts.clear()
```

**Step 2: Verify it works**

Run: `python -c "from src.data.memory_repo import MemoryRepository; r = MemoryRepository(); r.reset_all(); print('project:', r.get_project())"`
Expected: `project: None`

**Step 3: Commit**

```bash
git add src/data/memory_repo.py
git commit -m "feat(memory-repo): implement reset_all"
```

---

### Task 3: Implement reset_all in SupabaseRepository ✅

**Files:**
- Modify: `src/data/supabase_repo.py:164` (end of file)

**Step 1: Add the implementation**

Add after line 163:

```python
    # Reset methods
    def reset_all(self) -> None:
        """Delete all data. Order matters: children before parents (FK constraints)."""
        # Supabase requires a filter - use neq with impossible UUID to match all
        _ALL = "00000000-0000-0000-0000-000000000000"
        self.client.table("alerts").delete().neq("id", _ALL).execute()
        self.client.table("workflow_steps").delete().neq("id", _ALL).execute()
        self.client.table("piles").delete().neq("id", _ALL).execute()
        self.client.table("inverters").delete().neq("id", _ALL).execute()
        self.client.table("projects").delete().neq("id", _ALL).execute()
```

**Step 2: Verify syntax**

Run: `python -c "from src.data.supabase_repo import SupabaseRepository"`
Expected: No import errors (actual execution requires Supabase credentials)

**Step 3: Commit**

```bash
git add src/data/supabase_repo.py
git commit -m "feat(supabase-repo): implement reset_all with FK-safe delete order"
```

---

### Task 4: Wire up the UI button

**Files:**
- Modify: `src/ui/import_panel.py:82-84`

**Step 1: Replace the TODO with actual implementation**

Replace lines 82-84:

```python
            if st.button("Reset Project", type="secondary"):
                # TODO: Implement project reset
                st.info("Project reset not yet implemented")
```

With:

```python
            if st.button("Reset Project", type="secondary"):
                repo.reset_all()
                st.session_state.show_import = False
                st.rerun()
```

**Step 2: Manual test**

Run: `streamlit run src/app.py`
- Navigate to Import panel (with existing project)
- Expand "Advanced: Reset Project"
- Click "Reset Project"
- Expected: Returns to dashboard, then shows Drivelog import (no project state)

**Step 3: Commit**

```bash
git add src/ui/import_panel.py
git commit -m "feat(ui): wire up Reset Project button"
```

---

### Task 5: Update Issue 3 status

**Files:**
- Modify: `docs/plans/issues.md:108`

**Step 1: Mark issue resolved**

Change line 108 from:
```
**Status:** 🔴 Open
```

To:
```
**Status:** ✅ Resolved (2026-01-29) - Reset Project implemented
```

**Step 2: Commit**

```bash
git add docs/plans/issues.md
git commit -m "docs: mark Issue 3 as resolved"
```
