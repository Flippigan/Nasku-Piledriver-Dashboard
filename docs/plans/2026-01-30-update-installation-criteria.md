# Update Installation Criteria Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the computed `is_installed` property with a stored `pile_installed` field that trusts Drive Log values and computes values during Nasku import.

**Architecture:** Add `pile_installed` as a stored field on the `Pile` model with values "Yes", "No", or "Refusal". The `is_installed` property becomes a simple check of `pile_installed == "Yes"`. Drive Log imports pass through the existing `Pile_Installed` column; Nasku imports compute the value from `hammering_status` and `hammering_flag`.

**Tech Stack:** Python 3.11+, Pydantic v2, pandas, pytest

---

## Task 1: Add `compute_pile_installed` Helper Function

**Files:**
- Create: `src/import_/pile_installed.py`
- Test: `tests/test_pile_installed.py`

**Step 1: Write the failing tests**

```python
# tests/test_pile_installed.py
import pytest

from src.import_.pile_installed import compute_pile_installed


class TestComputePileInstalled:
    def test_refused_flag_returns_refusal(self):
        result = compute_pile_installed("COMPLETED", "REFUSED")
        assert result == "Refusal"

    def test_refused_flag_with_success_returns_refusal(self):
        result = compute_pile_installed("SUCCESS", "REFUSED")
        assert result == "Refusal"

    def test_completed_status_returns_yes(self):
        result = compute_pile_installed("COMPLETED", "GOOD")
        assert result == "Yes"

    def test_success_status_returns_yes(self):
        result = compute_pile_installed("SUCCESS", "NONE")
        assert result == "Yes"

    def test_completed_with_other_flag_returns_yes(self):
        result = compute_pile_installed("COMPLETED", "INCLINED")
        assert result == "Yes"

    def test_incomplete_status_returns_no(self):
        result = compute_pile_installed("INCOMPLETE_NO_FINISH_TIME", "UNSET")
        assert result == "No"

    def test_unattempted_status_returns_no(self):
        result = compute_pile_installed("UNATTEMPTED", "UNSET")
        assert result == "No"

    def test_none_values_return_no(self):
        result = compute_pile_installed(None, None)
        assert result == "No"

    def test_none_status_with_flag_returns_no(self):
        result = compute_pile_installed(None, "GOOD")
        assert result == "No"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_pile_installed.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.import_.pile_installed'"

**Step 3: Write minimal implementation**

```python
# src/import_/pile_installed.py
def compute_pile_installed(
    hammering_status: str | None,
    hammering_flag: str | None,
) -> str:
    """
    Compute Pile_Installed from hammering columns.
    Used during Nasku CSV import (which has no Pile_Installed column).

    Returns: "Yes", "No", or "Refusal"
    """
    if hammering_flag == "REFUSED":
        return "Refusal"

    if hammering_status in ("COMPLETED", "SUCCESS"):
        return "Yes"

    return "No"
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_pile_installed.py -v`
Expected: All 9 tests PASS

**Step 5: Commit**

```bash
git add src/import_/pile_installed.py tests/test_pile_installed.py
git commit -m "$(cat <<'EOF'
feat: add compute_pile_installed helper function

Adds logic to compute pile installation status from hammering columns.
Used during Nasku import where Pile_Installed is not present in source data.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Update Pile Model with `pile_installed` Field

**Files:**
- Modify: `src/data/models.py:26-42`
- Modify: `tests/test_models.py`

**Step 1: Write the failing tests**

Add these tests to `tests/test_models.py`:

```python
def test_pile_installed_yes_means_is_installed_true():
    pile = Pile(
        id=uuid4(),
        inverter_id=uuid4(),
        upn="12345",
        pile_installed="Yes",
    )
    assert pile.is_installed is True


def test_pile_installed_no_means_is_installed_false():
    pile = Pile(
        id=uuid4(),
        inverter_id=uuid4(),
        upn="12345",
        pile_installed="No",
    )
    assert pile.is_installed is False


def test_pile_installed_refusal_means_is_installed_false():
    pile = Pile(
        id=uuid4(),
        inverter_id=uuid4(),
        upn="12345",
        pile_installed="Refusal",
    )
    assert pile.is_installed is False


def test_pile_installed_defaults_to_no():
    pile = Pile(
        id=uuid4(),
        inverter_id=uuid4(),
        upn="12345",
    )
    assert pile.pile_installed == "No"
    assert pile.is_installed is False
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -v`
Expected: FAIL with "ValidationError" or "AttributeError" for `pile_installed`

**Step 3: Update the Pile model**

Replace the `Pile` class in `src/data/models.py`:

```python
class Pile(BaseModel):
    id: UUID
    inverter_id: UUID
    upn: str
    pile_installed: str = "No"  # "Yes", "No", or "Refusal"
    hammering_status: Optional[str] = None
    hammering_flag: Optional[str] = None
    hammering_time_sec: Optional[float] = None
    positioning_time_sec: Optional[float] = None
    driven_at: Optional[datetime] = None

    @computed_field
    @property
    def is_installed(self) -> bool:
        return self.pile_installed == "Yes"
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_models.py -v`
Expected: 4 new tests PASS

**Step 5: Update existing model tests for new behavior**

The existing tests `test_pile_installed_when_completed_and_good`, `test_pile_not_installed_when_incomplete`, and `test_pile_not_installed_when_bad_flag` need to be updated to set `pile_installed` explicitly:

```python
def test_pile_installed_when_completed_and_good():
    pile = Pile(
        id=uuid4(),
        inverter_id=uuid4(),
        upn="12345",
        pile_installed="Yes",
        hammering_status="COMPLETED",
        hammering_flag="GOOD",
        hammering_time_sec=150.5,
        positioning_time_sec=80.2,
        driven_at=datetime.now(),
    )
    assert pile.is_installed is True


def test_pile_not_installed_when_incomplete():
    pile = Pile(
        id=uuid4(),
        inverter_id=uuid4(),
        upn="12345",
        pile_installed="No",
        hammering_status="INCOMPLETE_NO_FINISH_TIME",
        hammering_flag="UNSET",
        hammering_time_sec=None,
        positioning_time_sec=None,
        driven_at=None,
    )
    assert pile.is_installed is False


def test_pile_not_installed_when_bad_flag():
    pile = Pile(
        id=uuid4(),
        inverter_id=uuid4(),
        upn="12345",
        pile_installed="No",
        hammering_status="COMPLETED",
        hammering_flag="BAD",
        hammering_time_sec=150.5,
        positioning_time_sec=80.2,
        driven_at=datetime.now(),
    )
    assert pile.is_installed is False
```

**Step 6: Run all model tests**

Run: `pytest tests/test_models.py -v`
Expected: All tests PASS

**Step 7: Commit**

```bash
git add src/data/models.py tests/test_models.py
git commit -m "$(cat <<'EOF'
feat: add pile_installed field to Pile model

Replace computed is_installed logic with stored pile_installed field.
The is_installed property now simply checks pile_installed == "Yes".
Supports three states: Yes, No, Refusal.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Update Drive Log Importer to Include `Pile_Installed`

**Files:**
- Modify: `src/import_/drivelog_importer.py`
- Modify: `tests/test_drivelog_importer.py`

**Step 1: Write the failing test**

Add to `tests/test_drivelog_importer.py`:

```python
DRIVELOG_WITH_PILE_INSTALLED = """Inverter,UPN,Hammering_Status,Hammering_Flag,Pile_Installed
1,41659,COMPLETED,GOOD,Yes
1,41660,COMPLETED,REFUSED,Refusal
2,50001,INCOMPLETE,UNSET,No
"""


class TestExtractPilesWithPileInstalled:
    def test_extracts_pile_installed_when_present(self):
        df = parse_drivelog(StringIO(DRIVELOG_WITH_PILE_INSTALLED))
        piles = extract_piles(df)

        assert piles["1"][0]["pile_installed"] == "Yes"
        assert piles["1"][1]["pile_installed"] == "Refusal"
        assert piles["2"][0]["pile_installed"] == "No"

    def test_defaults_pile_installed_to_no_when_missing(self):
        df = parse_drivelog(StringIO(SAMPLE_DRIVELOG))
        piles = extract_piles(df)

        # When Pile_Installed column is missing, should default to "No"
        assert piles["1"][0]["pile_installed"] == "No"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_drivelog_importer.py::TestExtractPilesWithPileInstalled -v`
Expected: FAIL with KeyError for 'pile_installed'

**Step 3: Update drivelog_importer.py**

Update `REQUIRED_COLUMNS` and `extract_piles`:

```python
REQUIRED_COLUMNS = ["Inverter", "UPN", "Hammering_Status", "Hammering_Flag"]
OPTIONAL_COLUMNS = ["Pile_Installed"]


def parse_drivelog(file: TextIO | BinaryIO) -> pd.DataFrame:
    df = parse_csv(file)
    validate_required_columns(df, REQUIRED_COLUMNS)

    # Keep required columns plus optional if present
    columns_to_keep = REQUIRED_COLUMNS.copy()
    for col in OPTIONAL_COLUMNS:
        if col in df.columns:
            columns_to_keep.append(col)

    df = df[columns_to_keep].copy()

    # Handle duplicate UPNs - keep first occurrence
    df = df.drop_duplicates(subset=["UPN"], keep="first")

    return df


def extract_piles(df: pd.DataFrame) -> dict[str, list[dict]]:
    df["Inverter"] = df["Inverter"].astype(str)
    has_pile_installed = "Pile_Installed" in df.columns

    result: dict[str, list[dict]] = {}
    for inverter_name, group in df.groupby("Inverter"):
        result[str(inverter_name)] = [
            {
                "upn": str(row["UPN"]),
                "hammering_status": row["Hammering_Status"] if pd.notna(row["Hammering_Status"]) else None,
                "hammering_flag": row["Hammering_Flag"] if pd.notna(row["Hammering_Flag"]) else None,
                "pile_installed": row["Pile_Installed"] if has_pile_installed and pd.notna(row["Pile_Installed"]) else "No",
            }
            for _, row in group.iterrows()
        ]
    return result
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_drivelog_importer.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/import_/drivelog_importer.py tests/test_drivelog_importer.py
git commit -m "$(cat <<'EOF'
feat: extract Pile_Installed column from Drive Log

Trust existing Pile_Installed values from Drive Log CSV.
Default to "No" when column is missing (backward compatibility).

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Update Nasku Importer to Compute `pile_installed`

**Files:**
- Modify: `src/import_/nasku_importer.py`
- Modify: `tests/test_nasku_importer.py`

**Step 1: Write the failing test**

Add to `tests/test_nasku_importer.py`:

```python
class TestExtractPileUpdatesWithPileInstalled:
    def test_computes_pile_installed_yes_for_completed(self):
        df = parse_nasku(StringIO(SAMPLE_NASKU))
        updates = extract_pile_updates(df)

        # COMPLETED + GOOD = Yes
        assert updates["27117"]["pile_installed"] == "Yes"
        # COMPLETED + GOOD = Yes
        assert updates["29852"]["pile_installed"] == "Yes"

    def test_computes_pile_installed_no_for_incomplete(self):
        df = parse_nasku(StringIO(SAMPLE_NASKU))
        updates = extract_pile_updates(df)

        # INCOMPLETE_NO_FINISH_TIME + UNSET = No
        assert updates["47574"]["pile_installed"] == "No"


NASKU_WITH_REFUSAL = """name,processedAt,positioningTime,hammeringTime,hammeringStatus,hammeringFlag
12345,2026-01-16T13:07:21.722-06:00,80000,17870,COMPLETED,REFUSED
"""


class TestExtractPileUpdatesRefusal:
    def test_computes_pile_installed_refusal_for_refused_flag(self):
        df = parse_nasku(StringIO(NASKU_WITH_REFUSAL))
        updates = extract_pile_updates(df)

        assert updates["12345"]["pile_installed"] == "Refusal"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_nasku_importer.py::TestExtractPileUpdatesWithPileInstalled -v`
Expected: FAIL with KeyError for 'pile_installed'

**Step 3: Update nasku_importer.py**

```python
from src.import_.pile_installed import compute_pile_installed

# ... existing code ...

def extract_pile_updates(df: pd.DataFrame) -> dict[str, dict]:
    updates = {}
    for _, row in df.iterrows():
        upn = str(row["name"])
        hammering_status = row["hammeringStatus"] if pd.notna(row["hammeringStatus"]) else None
        hammering_flag = row["hammeringFlag"] if pd.notna(row["hammeringFlag"]) else None

        updates[upn] = {
            "hammering_status": hammering_status,
            "hammering_flag": hammering_flag,
            "hammering_time_sec": _parse_time_ms(row["hammeringTime"]),
            "positioning_time_sec": _parse_time_ms(row["positioningTime"]),
            "driven_at": _parse_timestamp(row["processedAt"]),
            "pile_installed": compute_pile_installed(hammering_status, hammering_flag),
        }
    return updates
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_nasku_importer.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/import_/nasku_importer.py tests/test_nasku_importer.py
git commit -m "$(cat <<'EOF'
feat: compute pile_installed during Nasku import

Nasku CSV does not have Pile_Installed column, so compute it from
hammering_status and hammering_flag using the new helper function.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Update Import Service to Pass `pile_installed`

**Files:**
- Modify: `src/services/import_service.py`
- Modify: `tests/test_import_service.py`

**Step 1: Write the failing test**

Add to `tests/test_import_service.py`:

```python
class TestImportDrivelogPileInstalled:
    def test_passes_pile_installed_to_piles(self, mock_repo):
        drivelog_with_installed = """Inverter,UPN,Hammering_Status,Hammering_Flag,Pile_Installed
1,12345,COMPLETED,GOOD,Yes
1,12346,COMPLETED,REFUSED,Refusal
"""
        service = ImportService(mock_repo)
        service.import_drivelog(StringIO(drivelog_with_installed), "Test")

        # Check the piles that were saved
        saved_piles = mock_repo.save_piles.call_args[0][0]
        assert saved_piles[0].pile_installed == "Yes"
        assert saved_piles[1].pile_installed == "Refusal"


class TestImportNaskuPileInstalled:
    def test_updates_pile_installed_from_nasku(self, mock_repo):
        inverter_id = uuid4()
        existing_pile = Pile(
            id=uuid4(),
            inverter_id=inverter_id,
            upn="12345",
            pile_installed="No",
        )
        mock_repo.get_pile_by_upn.return_value = existing_pile
        mock_repo.update_pile.side_effect = lambda p: p
        mock_repo.get_piles_for_inverter.return_value = [existing_pile]
        mock_repo.get_inverters.return_value = [
            Inverter(
                id=inverter_id,
                project_id=uuid4(),
                name="1",
                total_piles=1,
                created_at=datetime.now(),
            )
        ]
        mock_repo.get_project.return_value = Project(
            id=uuid4(),
            name="Test",
            default_scan_threshold_pct=90,
            default_pile_rate=50,
            created_at=datetime.now(),
        )

        nasku_data = """name,processedAt,positioningTime,hammeringTime,hammeringStatus,hammeringFlag
12345,2026-01-16T13:07:21.722-06:00,80000,17870,COMPLETED,GOOD
"""
        service = ImportService(mock_repo)
        service.import_nasku(StringIO(nasku_data))

        # Verify pile_installed was updated
        updated_pile = mock_repo.update_pile.call_args[0][0]
        assert updated_pile.pile_installed == "Yes"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_import_service.py::TestImportDrivelogPileInstalled -v`
Expected: FAIL - pile_installed not being set

**Step 3: Update import_service.py**

Update `import_drivelog` method:

```python
# Create piles
pile_data = data.piles.get(inverter_name, [])
piles = [
    Pile(
        id=uuid4(),
        inverter_id=inverter.id,
        upn=p["upn"],
        pile_installed=p["pile_installed"],
        hammering_status=p["hammering_status"],
        hammering_flag=p["hammering_flag"],
    )
    for p in pile_data
]
```

Update `import_nasku` method:

```python
# Update piles
for upn, update in data.updates.items():
    inverter_id = upn_to_inverter[upn]
    pile = self.repo.get_pile_by_upn(inverter_id, upn)
    if pile:
        pile.hammering_status = update["hammering_status"]
        pile.hammering_flag = update["hammering_flag"]
        pile.hammering_time_sec = update["hammering_time_sec"]
        pile.positioning_time_sec = update["positioning_time_sec"]
        pile.driven_at = update["driven_at"]
        pile.pile_installed = update["pile_installed"]
        self.repo.update_pile(pile)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_import_service.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/services/import_service.py tests/test_import_service.py
git commit -m "$(cat <<'EOF'
feat: pass pile_installed through import service

Drive Log import uses Pile_Installed from CSV.
Nasku import uses computed pile_installed value.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Update Database Schema

**Files:**
- Modify: `scripts/setup_database.sql`

**Step 1: Document the schema change**

Add the `pile_installed` column to the piles table. The schema change is:

```sql
-- Add to piles table definition:
pile_installed TEXT DEFAULT 'No',
```

**Step 2: Update setup_database.sql**

```sql
-- Piles table
CREATE TABLE piles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inverter_id UUID NOT NULL REFERENCES inverters(id) ON DELETE CASCADE,
    upn TEXT NOT NULL,
    pile_installed TEXT DEFAULT 'No',
    hammering_status TEXT,
    hammering_flag TEXT,
    hammering_time_sec DOUBLE PRECISION,
    positioning_time_sec DOUBLE PRECISION,
    driven_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(inverter_id, upn)
);
```

**Step 3: Create migration script for existing databases**

Create `scripts/migrations/001_add_pile_installed.sql`:

```sql
-- Migration: Add pile_installed column to piles table
-- Run this on existing databases to add the new column

ALTER TABLE piles ADD COLUMN IF NOT EXISTS pile_installed TEXT DEFAULT 'No';

-- Backfill existing data based on hammering_status and hammering_flag
UPDATE piles
SET pile_installed = CASE
    WHEN hammering_flag = 'REFUSED' THEN 'Refusal'
    WHEN hammering_status IN ('COMPLETED', 'SUCCESS') THEN 'Yes'
    ELSE 'No'
END
WHERE pile_installed IS NULL OR pile_installed = 'No';
```

**Step 4: Commit**

```bash
mkdir -p scripts/migrations
git add scripts/setup_database.sql scripts/migrations/001_add_pile_installed.sql
git commit -m "$(cat <<'EOF'
feat: add pile_installed column to database schema

Add pile_installed column to piles table.
Include migration script for existing databases with backfill logic.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Update Repository Implementations

**Files:**
- Modify: `src/data/supabase_repo.py:86-101`
- Modify: `src/data/memory_repo.py:57-69`
- Modify: `tests/conftest.py:33-43, 45-57`
- Modify: `tests/test_progress.py:37-47`

**Step 1: Update conftest.py fixtures**

```python
@pytest.fixture
def installed_pile(sample_inverter):
    return Pile(
        id=uuid4(),
        inverter_id=sample_inverter.id,
        upn="12345",
        pile_installed="Yes",
        hammering_status="COMPLETED",
        hammering_flag="GOOD",
        hammering_time_sec=150.5,
        positioning_time_sec=80.2,
        driven_at=datetime.now(),
    )


@pytest.fixture
def uninstalled_pile(sample_inverter):
    return Pile(
        id=uuid4(),
        inverter_id=sample_inverter.id,
        upn="67890",
        pile_installed="No",
        hammering_status="INCOMPLETE_NO_FINISH_TIME",
        hammering_flag="UNSET",
        hammering_time_sec=None,
        positioning_time_sec=None,
        driven_at=None,
    )
```

**Step 2: Update test_progress.py make_pile helper**

```python
def make_pile(inverter_id, upn, installed=True, driven_at=None, hammering_sec=100, positioning_sec=50):
    return Pile(
        id=uuid4(),
        inverter_id=inverter_id,
        upn=upn,
        pile_installed="Yes" if installed else "No",
        hammering_status="COMPLETED" if installed else "INCOMPLETE",
        hammering_flag="GOOD" if installed else "UNSET",
        hammering_time_sec=hammering_sec if installed else None,
        positioning_time_sec=positioning_sec if installed else None,
        driven_at=driven_at or (datetime.now() if installed else None),
    )
```

**Step 3: Update memory_repo.py demo data**

```python
# Create piles
for i in range(total):
    is_installed = i < installed_count
    pile = Pile(
        id=uuid4(),
        inverter_id=inv.id,
        upn=f"{name}-{i+1:04d}",
        pile_installed="Yes" if is_installed else "No",
        hammering_status="COMPLETED" if is_installed else "INCOMPLETE",
        hammering_flag="GOOD" if is_installed else "UNSET",
        hammering_time_sec=150.0 if is_installed else None,
        positioning_time_sec=80.0 if is_installed else None,
        driven_at=datetime.now() if is_installed else None,
    )
    self._piles[pile.id] = pile
```

**Step 4: Update supabase_repo.py exclude list**

The `is_installed` computed field is still excluded from saves. No change needed since we're adding `pile_installed` as a stored field (not computed).

**Step 5: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/data/memory_repo.py tests/conftest.py tests/test_progress.py
git commit -m "$(cat <<'EOF'
chore: update test fixtures and memory repo for pile_installed

Update all test helpers and demo data to use the new pile_installed field.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Run Full Test Suite and Verify

**Files:**
- None (verification only)

**Step 1: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: All tests PASS

**Step 2: Run the app in demo mode**

Run: `streamlit run src/app.py`
Expected: Dashboard loads with demo data showing correct progress percentages

**Step 3: Verify integration test**

Run: `pytest tests/test_integration.py -v`
Expected: All integration tests PASS

**Step 4: Final commit if any fixes needed**

If any tests failed and were fixed, commit those fixes.

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
