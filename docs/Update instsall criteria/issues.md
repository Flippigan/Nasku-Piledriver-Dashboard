# Issues: Update Installation Criteria

## Issue #1: All inverters showing no progress

**Status:** Resolved
**Reported:** 2026-01-30
**Resolved:** 2026-01-30
**Severity:** High

### Description

After implementing the `pile_installed` field changes, all inverters were showing no progress (0%), whereas previously a select few were showing correct progress percentages.

### Root Cause

The production Supabase database was created before the `pile_installed` column was added to the schema. When the `SupabaseRepository` fetched piles, the column was missing, causing Pydantic to use the default value `"No"` for all piles. This made `is_installed` return `False` for every pile, resulting in 0% progress across all inverters.

### Resolution

Ran the migration script on the production Supabase database:

```sql
-- From scripts/migrations/001_add_pile_installed.sql
ALTER TABLE piles ADD COLUMN IF NOT EXISTS pile_installed TEXT DEFAULT 'No';

UPDATE piles
SET pile_installed = CASE
    WHEN hammering_flag = 'REFUSED' THEN 'Refusal'
    WHEN hammering_status IN ('COMPLETED', 'SUCCESS') THEN 'Yes'
    ELSE 'No'
END
WHERE pile_installed IS NULL OR pile_installed = 'No';
```

Additionally, updated outdated comments in `src/data/supabase_repo.py` that incorrectly stated `is_installed` was derived from `hammering_status/flag` (now derived from `pile_installed`).

### Verification

- Dashboard now displays correct progress percentages for all inverters
- All 80 tests continue to pass

### Lessons Learned

- When adding new columns that change how computed properties work, migrations must be run on existing databases before deploying the code change
- Consider adding a startup check or warning when expected columns are missing from the database
