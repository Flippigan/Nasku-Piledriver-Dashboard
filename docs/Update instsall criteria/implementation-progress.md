# Implementation Progress: Update Installation Criteria

**Plan:** `docs/plans/2026-01-30-update-installation-criteria.md`
**Branch:** `feature/windows-exe-build`
**Started:** 2026-01-30

---

## Summary

Replacing the computed `is_installed` property with a stored `pile_installed` field that:
- Trusts Drive Log CSV values when present
- Computes values during Nasku import from `hammering_status` + `hammering_flag`

---

## Task Progress

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1 | Add `compute_pile_installed` helper function | Done | `0cad085` |
| 2 | Update Pile model with `pile_installed` field | Done | `ea220f3` |
| 3 | Update Drive Log importer for `Pile_Installed` | Done | `3e940b7` |
| 4 | Update Nasku importer to compute `pile_installed` | Done | `0dae089` |
| 5 | Update Import Service for `pile_installed` | Done | `b0e2f5f` |
| 6 | Update database schema | Done | `43617e7` |
| 7 | Update repository implementations and test fixtures | Done | `99b245e` |
| 8 | Run full test suite and verify | Done | - |

---

## Batch 1 Details (Tasks 1-3)

### Task 1: Add `compute_pile_installed` helper function

**Files created:**
- `src/import_/pile_installed.py` - Helper function
- `tests/test_pile_installed.py` - 9 tests

**Logic:**
```python
def compute_pile_installed(hammering_status, hammering_flag) -> str:
    if hammering_flag == "REFUSED":
        return "Refusal"
    if hammering_status in ("COMPLETED", "SUCCESS"):
        return "Yes"
    return "No"
```

**Tests:** 9/9 passing

---

### Task 2: Update Pile model with `pile_installed` field

**Files modified:**
- `src/data/models.py` - Added `pile_installed` field, simplified `is_installed` property
- `tests/test_models.py` - Added 4 new tests, updated 3 existing tests

**Changes:**
- Added `pile_installed: str = "No"` field (values: "Yes", "No", "Refusal")
- Changed `is_installed` from computed logic to simple check: `pile_installed == "Yes"`

**Tests:** 11/11 passing

---

### Task 3: Update Drive Log importer for `Pile_Installed`

**Files modified:**
- `src/import_/drivelog_importer.py` - Added `OPTIONAL_COLUMNS`, updated `parse_drivelog` and `extract_piles`
- `tests/test_drivelog_importer.py` - Added 2 new tests

**Changes:**
- `Pile_Installed` column is now extracted when present in CSV
- Defaults to "No" when column is missing (backward compatibility)

**Tests:** 8/8 passing

---

## Batch 2 Details (Tasks 4-7)

### Task 4: Update Nasku importer to compute `pile_installed`

**Files modified:**
- `src/import_/nasku_importer.py` - Import `compute_pile_installed`, add to `extract_pile_updates()`
- `tests/test_nasku_importer.py` - Added 3 new tests

**Changes:**
- Import `compute_pile_installed` from `src.import_.pile_installed`
- Extract `hammering_status` and `hammering_flag` before building dict
- Add `pile_installed` key computed from those values

**Tests:** 10/10 passing

---

### Task 5: Update Import Service for `pile_installed`

**Files modified:**
- `src/services/import_service.py` - Pass `pile_installed` in both import methods
- `tests/test_import_service.py` - Added 2 new tests

**Changes:**
- `import_drivelog`: Pass `pile_installed=p["pile_installed"]` when creating Pile objects
- `import_nasku`: Set `pile.pile_installed = update["pile_installed"]` when updating piles

**Tests:** 7/7 passing

---

### Task 6: Update database schema

**Files modified:**
- `scripts/setup_database.sql` - Added `pile_installed TEXT DEFAULT 'No'` to piles table

**Files created:**
- `scripts/migrations/001_add_pile_installed.sql` - Migration with backfill logic

**Migration logic:**
```sql
ALTER TABLE piles ADD COLUMN IF NOT EXISTS pile_installed TEXT DEFAULT 'No';

UPDATE piles SET pile_installed = CASE
    WHEN hammering_flag = 'REFUSED' THEN 'Refusal'
    WHEN hammering_status IN ('COMPLETED', 'SUCCESS') THEN 'Yes'
    ELSE 'No'
END
WHERE pile_installed IS NULL OR pile_installed = 'No';
```

---

### Task 7: Update test fixtures and memory repo

**Files modified:**
- `tests/conftest.py` - Added `pile_installed` to `installed_pile` and `uninstalled_pile` fixtures
- `tests/test_progress.py` - Updated `make_pile()` helper to set `pile_installed`
- `tests/test_integration.py` - Added `Pile_Installed` column to DRIVELOG constant
- `src/data/memory_repo.py` - Updated demo data to include `pile_installed`

---

### Task 8: Full test suite verification

**Command:** `pytest tests/ -v`
**Result:** 80/80 tests passing

---

## Summary of Changes

| File | Change |
|------|--------|
| `src/import_/pile_installed.py` | NEW - Helper function to compute pile_installed |
| `src/data/models.py` | Add `pile_installed` field, update `is_installed` property |
| `src/import_/drivelog_importer.py` | Extract `Pile_Installed` column from CSV |
| `src/import_/nasku_importer.py` | Compute `pile_installed` using helper |
| `src/services/import_service.py` | Pass `pile_installed` to Pile model |
| `scripts/setup_database.sql` | Add `pile_installed` column to schema |
| `scripts/migrations/001_add_pile_installed.sql` | NEW - Migration for existing DBs |
| `src/data/memory_repo.py` | Update demo data |
| `tests/test_pile_installed.py` | NEW - Tests for helper function |
| `tests/test_models.py` | Update for new behavior |
| `tests/test_drivelog_importer.py` | Add tests for Pile_Installed extraction |
| `tests/test_nasku_importer.py` | Add tests for computed pile_installed |
| `tests/test_import_service.py` | Add tests for pile_installed passthrough |
| `tests/conftest.py` | Update fixtures |
| `tests/test_progress.py` | Update make_pile helper |
| `tests/test_integration.py` | Update DRIVELOG constant |

---

## Implementation Complete

All 8 tasks completed. Full test suite passing (80/80 tests).

---

## Post-Implementation Fix: Production Database Migration

**Date:** 2026-01-30
**Issue:** All inverters showing 0% progress in production

### Problem

After deploying the `pile_installed` changes, all inverters displayed 0% progress. The production Supabase database was created before the schema change, so the `pile_installed` column was missing. Pydantic defaulted all values to `"No"`, causing `is_installed` to return `False` for every pile.

### Resolution

1. Ran migration SQL on production Supabase:
   ```sql
   ALTER TABLE piles ADD COLUMN IF NOT EXISTS pile_installed TEXT DEFAULT 'No';

   UPDATE piles
   SET pile_installed = CASE
       WHEN hammering_flag = 'REFUSED' THEN 'Refusal'
       WHEN hammering_status IN ('COMPLETED', 'SUCCESS') THEN 'Yes'
       ELSE 'No'
   END
   WHERE pile_installed IS NULL OR pile_installed = 'No';
   ```

2. Updated outdated comments in `src/data/supabase_repo.py` (lines 87, 93) to reflect that `is_installed` is now derived from `pile_installed`, not `hammering_status/flag`.

### Verification

- Dashboard displays correct progress percentages
- All 80 tests passing

### Lesson Learned

When adding columns that affect computed properties, run database migrations before deploying code changes to avoid temporary regressions.
