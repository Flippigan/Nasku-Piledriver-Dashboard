# Inverter Tracker Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Streamlit desktop app (.exe) for VDC engineers to track pile installation progress and workflow status across solar site inverters.

**Architecture:** Python Streamlit app with a data layer abstraction over Supabase (PostgreSQL). CSV imports feed the database, dashboard displays real-time progress with color-coded status cards. Alert system notifies users when milestones are reached.

**Tech Stack:** Python 3.11+, Streamlit, Supabase (supabase-py), pandas, PyInstaller

---

## Progress Tracking

| Task | Description | Status | Commit |
|------|-------------|--------|--------|
| 1 | Project Setup and Models | ✅ Complete | `000a4cc` |
| 2 | CSV Parser Module | ✅ Complete | `8daafed` |
| 3 | Drivelog Importer | ✅ Complete | `e14915b` |
| 4 | Nasku Importer | ✅ Complete | `980aa05` |
| 5 | Progress and ETA Calculation Service | ✅ Complete | `05311e2` |
| 6 | Alert Service | ✅ Complete | `a834368` |
| 7 | Repository Interface and Supabase Implementation | ✅ Complete | `fbd71b8` |
| 8 | Workflow Step Constants and Factory | ✅ Complete | `d859f5f` |
| 9 | Import Orchestration Service | ✅ Complete | `48408cc` |
| 10 | Supabase Database Setup Script | ✅ Complete | `770a568` |
| 11 | Streamlit UI - Dashboard Grid | ⏳ Pending | |
| 12 | Streamlit UI - Expanded Card with Workflow | ⏳ Pending | |
| 13 | Streamlit UI - Import Panel | ⏳ Pending | |
| 14 | Streamlit UI - Settings Panel | ⏳ Pending | |
| 15 | PyInstaller Packaging | ⏳ Pending | |
| 16 | Integration Testing and Final Polish | ⏳ Pending | |

**Last Updated:** 2026-01-29
**Tests Passing:** 58/58

---

## Project Structure

```
inverter_tracker/
├── src/
│   ├── __init__.py
│   ├── app.py                    # Streamlit entry point
│   ├── data/
│   │   ├── __init__.py
│   │   ├── models.py             # Pydantic models for all entities
│   │   ├── repository.py         # Data layer abstraction (interface)
│   │   └── supabase_repo.py      # Supabase implementation
│   ├── import/
│   │   ├── __init__.py
│   │   ├── csv_parser.py         # CSV parsing logic
│   │   ├── drivelog_importer.py  # Drivelog import logic
│   │   └── nasku_importer.py     # Nasku import logic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── progress.py           # Progress & ETA calculations
│   │   └── alerts.py             # Alert management
│   └── ui/
│       ├── __init__.py
│       ├── dashboard.py          # Main grid view
│       ├── card.py               # Inverter card component
│       ├── expanded_card.py      # Expanded card with workflow
│       └── settings.py           # Settings panel
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures
│   ├── test_models.py
│   ├── test_csv_parser.py
│   ├── test_drivelog_importer.py
│   ├── test_nasku_importer.py
│   ├── test_progress.py
│   ├── test_alerts.py
│   └── test_repository.py
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## Task 1: Project Setup and Models

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `src/__init__.py`
- Create: `src/data/__init__.py`
- Create: `src/data/models.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_models.py`

**Step 1: Create requirements.txt**

```txt
streamlit>=1.31.0
supabase>=2.0.0
pandas>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-cov>=4.0.0
```

**Step 2: Create pyproject.toml**

```toml
[project]
name = "inverter-tracker"
version = "1.0.0"
description = "Dashboard for tracking pile installation progress"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

**Step 3: Create .env.example**

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

**Step 4: Create src/__init__.py and src/data/__init__.py**

```python
# Empty init files
```

**Step 5: Write failing test for models**

Create `tests/__init__.py` (empty) and `tests/test_models.py`:

```python
import pytest
from datetime import datetime, date
from uuid import uuid4

from src.data.models import Project, Inverter, Pile, WorkflowStep, Alert


def test_project_has_required_fields():
    project = Project(
        id=uuid4(),
        name="Solar Site Alpha",
        default_scan_threshold_pct=90,
        default_pile_rate=50,
        created_at=datetime.now(),
    )
    assert project.name == "Solar Site Alpha"
    assert project.default_scan_threshold_pct == 90
    assert project.default_pile_rate == 50


def test_inverter_has_required_fields():
    project_id = uuid4()
    inverter = Inverter(
        id=uuid4(),
        project_id=project_id,
        name="Inverter 1",
        total_piles=2000,
        scan_threshold_override=None,
        milestone_thresholds=[50, 75, 90],
        created_at=datetime.now(),
    )
    assert inverter.name == "Inverter 1"
    assert inverter.total_piles == 2000
    assert inverter.milestone_thresholds == [50, 75, 90]


def test_pile_installed_when_completed_and_good():
    pile = Pile(
        id=uuid4(),
        inverter_id=uuid4(),
        upn="12345",
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
        hammering_status="COMPLETED",
        hammering_flag="BAD",
        hammering_time_sec=150.5,
        positioning_time_sec=80.2,
        driven_at=datetime.now(),
    )
    assert pile.is_installed is False


def test_workflow_step_has_required_fields():
    step = WorkflowStep(
        id=uuid4(),
        inverter_id=uuid4(),
        step_name="First Scan",
        step_order=1,
        is_complete=False,
        completed_at=None,
        due_date=date(2026, 2, 15),
        assigned_engineer="Sarah",
    )
    assert step.step_name == "First Scan"
    assert step.step_order == 1
    assert step.is_complete is False


def test_alert_has_required_fields():
    alert = Alert(
        id=uuid4(),
        inverter_id=uuid4(),
        alert_type="milestone_reached",
        threshold_value=75,
        acknowledged=False,
        created_at=datetime.now(),
    )
    assert alert.alert_type == "milestone_reached"
    assert alert.threshold_value == 75
    assert alert.acknowledged is False
```

**Step 6: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.data.models'"

**Step 7: Write minimal implementation**

Create `src/data/models.py`:

```python
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, computed_field


class Project(BaseModel):
    id: UUID
    name: str
    default_scan_threshold_pct: int
    default_pile_rate: int
    created_at: datetime


class Inverter(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    total_piles: int
    scan_threshold_override: Optional[int] = None
    milestone_thresholds: list[int] = [50, 75, 90]
    created_at: datetime


class Pile(BaseModel):
    id: UUID
    inverter_id: UUID
    upn: str
    hammering_status: Optional[str] = None
    hammering_flag: Optional[str] = None
    hammering_time_sec: Optional[float] = None
    positioning_time_sec: Optional[float] = None
    driven_at: Optional[datetime] = None

    @computed_field
    @property
    def is_installed(self) -> bool:
        return (
            self.hammering_status == "COMPLETED"
            and self.hammering_flag == "GOOD"
        )


class WorkflowStep(BaseModel):
    id: UUID
    inverter_id: UUID
    step_name: str
    step_order: int
    is_complete: bool = False
    completed_at: Optional[datetime] = None
    due_date: Optional[date] = None
    assigned_engineer: Optional[str] = None


class Alert(BaseModel):
    id: UUID
    inverter_id: UUID
    alert_type: str
    threshold_value: int
    acknowledged: bool = False
    created_at: datetime
```

**Step 8: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS (all 7 tests)

**Step 9: Create tests/conftest.py with shared fixtures**

```python
import pytest
from datetime import datetime, date
from uuid import uuid4

from src.data.models import Project, Inverter, Pile, WorkflowStep, Alert


@pytest.fixture
def sample_project():
    return Project(
        id=uuid4(),
        name="Solar Site Alpha",
        default_scan_threshold_pct=90,
        default_pile_rate=50,
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_inverter(sample_project):
    return Inverter(
        id=uuid4(),
        project_id=sample_project.id,
        name="Inverter 1",
        total_piles=2000,
        scan_threshold_override=None,
        milestone_thresholds=[50, 75, 90],
        created_at=datetime.now(),
    )


@pytest.fixture
def installed_pile(sample_inverter):
    return Pile(
        id=uuid4(),
        inverter_id=sample_inverter.id,
        upn="12345",
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
        hammering_status="INCOMPLETE_NO_FINISH_TIME",
        hammering_flag="UNSET",
        hammering_time_sec=None,
        positioning_time_sec=None,
        driven_at=None,
    )
```

**Step 10: Run all tests**

Run: `pytest tests/ -v`
Expected: PASS

**Step 11: Commit**

```bash
git add requirements.txt pyproject.toml .env.example src/ tests/
git commit -m "feat: add project setup and Pydantic models

- Project, Inverter, Pile, WorkflowStep, Alert models
- Pile.is_installed computed property for installation logic
- Test fixtures for common test scenarios"
```

---

## Task 2: CSV Parser Module

**Files:**
- Create: `src/import/__init__.py`
- Create: `src/import/csv_parser.py`
- Create: `tests/test_csv_parser.py`

**Step 1: Write failing test for CSV parser**

Create `tests/test_csv_parser.py`:

```python
import pytest
import pandas as pd
from io import StringIO

from src.import_.csv_parser import (
    parse_csv,
    validate_required_columns,
    MissingColumnsError,
)


class TestValidateRequiredColumns:
    def test_passes_when_all_columns_present(self):
        df = pd.DataFrame({"name": ["a"], "status": ["b"], "flag": ["c"]})
        # Should not raise
        validate_required_columns(df, ["name", "status"])

    def test_raises_when_column_missing(self):
        df = pd.DataFrame({"name": ["a"], "status": ["b"]})
        with pytest.raises(MissingColumnsError) as exc:
            validate_required_columns(df, ["name", "status", "flag"])
        assert "flag" in str(exc.value)

    def test_raises_with_multiple_missing_columns(self):
        df = pd.DataFrame({"name": ["a"]})
        with pytest.raises(MissingColumnsError) as exc:
            validate_required_columns(df, ["name", "status", "flag"])
        assert "status" in str(exc.value)
        assert "flag" in str(exc.value)


class TestParseCsv:
    def test_parses_valid_csv(self):
        csv_content = "name,value\na,1\nb,2"
        df = parse_csv(StringIO(csv_content))
        assert len(df) == 2
        assert list(df.columns) == ["name", "value"]

    def test_raises_on_empty_file(self):
        with pytest.raises(ValueError, match="empty"):
            parse_csv(StringIO(""))

    def test_handles_whitespace_in_headers(self):
        csv_content = " name , value \na,1"
        df = parse_csv(StringIO(csv_content))
        assert list(df.columns) == ["name", "value"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_csv_parser.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/import_/__init__.py` (note: using `import_` with underscore since `import` is reserved):

```python
# Empty init
```

Create `src/import_/csv_parser.py`:

```python
from typing import BinaryIO, TextIO
import pandas as pd


class MissingColumnsError(Exception):
    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(f"Missing required columns: {', '.join(missing)}")


def validate_required_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise MissingColumnsError(missing)


def parse_csv(file: TextIO | BinaryIO) -> pd.DataFrame:
    df = pd.read_csv(file)

    if df.empty and len(df.columns) == 0:
        raise ValueError("File is empty")

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    return df
```

**Step 4: Update test import path**

Update `tests/test_csv_parser.py` imports:

```python
from src.import_.csv_parser import (
    parse_csv,
    validate_required_columns,
    MissingColumnsError,
)
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_csv_parser.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/import_/ tests/test_csv_parser.py
git commit -m "feat: add CSV parser with column validation

- parse_csv function with empty file detection
- validate_required_columns with MissingColumnsError
- Strips whitespace from column headers"
```

---

## Task 3: Drivelog Importer

**Files:**
- Create: `src/import_/drivelog_importer.py`
- Create: `tests/test_drivelog_importer.py`

**Step 1: Write failing test for drivelog importer**

Create `tests/test_drivelog_importer.py`:

```python
import pytest
import pandas as pd
from io import StringIO
from uuid import uuid4

from src.import_.drivelog_importer import (
    parse_drivelog,
    extract_inverters,
    extract_piles,
    DrivelogData,
)
from src.import_.csv_parser import MissingColumnsError


SAMPLE_DRIVELOG = """OBJECTID,Inverter,Row,Table_,UPN,Hammering_Status,Hammering_Flag,Other_Column
1,1,40,360,41659,COMPLETED,GOOD,ignored
2,1,41,361,41660,COMPLETED,GOOD,ignored
3,2,10,100,50001,INCOMPLETE,UNSET,ignored
4,2,11,101,50002,COMPLETED,BAD,ignored
"""


class TestParseDrivelog:
    def test_extracts_required_columns_only(self):
        result = parse_drivelog(StringIO(SAMPLE_DRIVELOG))
        assert set(result.columns) == {"Inverter", "UPN", "Hammering_Status", "Hammering_Flag"}

    def test_raises_on_missing_required_column(self):
        bad_csv = "OBJECTID,Row,UPN\n1,40,41659"
        with pytest.raises(MissingColumnsError) as exc:
            parse_drivelog(StringIO(bad_csv))
        assert "Inverter" in str(exc.value)

    def test_handles_duplicate_upns_keeps_first(self):
        csv_with_dupe = """Inverter,UPN,Hammering_Status,Hammering_Flag
1,12345,COMPLETED,GOOD
1,12345,INCOMPLETE,UNSET
"""
        result = parse_drivelog(StringIO(csv_with_dupe))
        assert len(result) == 1
        assert result.iloc[0]["Hammering_Status"] == "COMPLETED"


class TestExtractInverters:
    def test_extracts_unique_inverters_with_pile_counts(self):
        df = parse_drivelog(StringIO(SAMPLE_DRIVELOG))
        inverters = extract_inverters(df)

        assert len(inverters) == 2
        assert inverters["1"] == 2  # Inverter 1 has 2 piles
        assert inverters["2"] == 2  # Inverter 2 has 2 piles


class TestExtractPiles:
    def test_extracts_piles_grouped_by_inverter(self):
        df = parse_drivelog(StringIO(SAMPLE_DRIVELOG))
        piles = extract_piles(df)

        assert "1" in piles
        assert "2" in piles
        assert len(piles["1"]) == 2
        assert piles["1"][0]["upn"] == "41659"
        assert piles["1"][0]["hammering_status"] == "COMPLETED"
        assert piles["1"][0]["hammering_flag"] == "GOOD"


class TestDrivelogData:
    def test_full_parse_returns_structured_data(self):
        data = DrivelogData.from_csv(StringIO(SAMPLE_DRIVELOG))

        assert len(data.inverters) == 2
        assert data.inverters["1"] == 2
        assert len(data.piles["1"]) == 2
        assert len(data.piles["2"]) == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_drivelog_importer.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/import_/drivelog_importer.py`:

```python
from dataclasses import dataclass
from typing import TextIO, BinaryIO
import pandas as pd

from src.import_.csv_parser import parse_csv, validate_required_columns


REQUIRED_COLUMNS = ["Inverter", "UPN", "Hammering_Status", "Hammering_Flag"]


@dataclass
class PileData:
    upn: str
    hammering_status: str | None
    hammering_flag: str | None


@dataclass
class DrivelogData:
    inverters: dict[str, int]  # inverter_name -> pile_count
    piles: dict[str, list[dict]]  # inverter_name -> list of pile dicts

    @classmethod
    def from_csv(cls, file: TextIO | BinaryIO) -> "DrivelogData":
        df = parse_drivelog(file)
        return cls(
            inverters=extract_inverters(df),
            piles=extract_piles(df),
        )


def parse_drivelog(file: TextIO | BinaryIO) -> pd.DataFrame:
    df = parse_csv(file)
    validate_required_columns(df, REQUIRED_COLUMNS)

    # Keep only required columns
    df = df[REQUIRED_COLUMNS].copy()

    # Handle duplicate UPNs - keep first occurrence
    df = df.drop_duplicates(subset=["UPN"], keep="first")

    return df


def extract_inverters(df: pd.DataFrame) -> dict[str, int]:
    # Convert Inverter to string for consistent keys
    df["Inverter"] = df["Inverter"].astype(str)
    return df.groupby("Inverter").size().to_dict()


def extract_piles(df: pd.DataFrame) -> dict[str, list[dict]]:
    df["Inverter"] = df["Inverter"].astype(str)

    result: dict[str, list[dict]] = {}
    for inverter_name, group in df.groupby("Inverter"):
        result[str(inverter_name)] = [
            {
                "upn": str(row["UPN"]),
                "hammering_status": row["Hammering_Status"] if pd.notna(row["Hammering_Status"]) else None,
                "hammering_flag": row["Hammering_Flag"] if pd.notna(row["Hammering_Flag"]) else None,
            }
            for _, row in group.iterrows()
        ]
    return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_drivelog_importer.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/import_/drivelog_importer.py tests/test_drivelog_importer.py
git commit -m "feat: add drivelog CSV importer

- Extracts only required columns (Inverter, UPN, status, flag)
- Groups piles by inverter with counts
- Handles duplicate UPNs by keeping first occurrence"
```

---

## Task 4: Nasku Importer

**Files:**
- Create: `src/import_/nasku_importer.py`
- Create: `tests/test_nasku_importer.py`

**Step 1: Write failing test for nasku importer**

Create `tests/test_nasku_importer.py`:

```python
import pytest
import pandas as pd
from io import StringIO
from datetime import datetime

from src.import_.nasku_importer import (
    parse_nasku,
    validate_upns_exist,
    extract_pile_updates,
    NaskuData,
    UnmatchedUpnError,
)
from src.import_.csv_parser import MissingColumnsError


SAMPLE_NASKU = """name,processedAt,machine,positioningTime,hammeringTime,hammeringStatus,hammeringFlag,resultEasting,resultNorthing,resultAltitude
27117,2026-01-16T13:07:21.722-06:00[America/Chicago],Machine_4,null,17870,COMPLETED,GOOD,689158.07,111718.79,276.68
29852,2026-01-16T13:37:11.499-06:00[America/Chicago],Machine_4,80500,165181,COMPLETED,GOOD,689181.83,111710.68,276.21
47574,2026-01-03T07:27:51.821-06:00[America/Chicago],Machine_3,null,147725,INCOMPLETE_NO_FINISH_TIME,UNSET,null,null,null
"""


class TestParseNasku:
    def test_extracts_required_columns(self):
        result = parse_nasku(StringIO(SAMPLE_NASKU))
        expected_cols = {"name", "processedAt", "positioningTime", "hammeringTime",
                        "hammeringStatus", "hammeringFlag"}
        assert expected_cols.issubset(set(result.columns))

    def test_raises_on_missing_column(self):
        bad_csv = "name,processedAt\n12345,2026-01-16"
        with pytest.raises(MissingColumnsError) as exc:
            parse_nasku(StringIO(bad_csv))
        assert "hammeringStatus" in str(exc.value)


class TestValidateUpnsExist:
    def test_passes_when_all_upns_exist(self):
        nasku_upns = {"27117", "29852"}
        existing_upns = {"27117", "29852", "99999"}
        # Should not raise
        validate_upns_exist(nasku_upns, existing_upns)

    def test_raises_when_upn_not_found(self):
        nasku_upns = {"27117", "29852", "UNKNOWN"}
        existing_upns = {"27117", "29852"}
        with pytest.raises(UnmatchedUpnError) as exc:
            validate_upns_exist(nasku_upns, existing_upns)
        assert "UNKNOWN" in exc.value.unmatched_upns


class TestExtractPileUpdates:
    def test_extracts_update_data(self):
        df = parse_nasku(StringIO(SAMPLE_NASKU))
        updates = extract_pile_updates(df)

        assert len(updates) == 3
        assert updates["27117"]["hammering_status"] == "COMPLETED"
        assert updates["27117"]["hammering_flag"] == "GOOD"
        assert updates["27117"]["hammering_time_sec"] == 17.870  # Converted from ms
        assert updates["27117"]["positioning_time_sec"] is None  # Was "null"

    def test_parses_timestamp(self):
        df = parse_nasku(StringIO(SAMPLE_NASKU))
        updates = extract_pile_updates(df)

        assert updates["27117"]["driven_at"] is not None
        assert isinstance(updates["27117"]["driven_at"], datetime)


class TestNaskuData:
    def test_from_csv_returns_structured_data(self):
        data = NaskuData.from_csv(StringIO(SAMPLE_NASKU))

        assert len(data.updates) == 3
        assert "27117" in data.updates
        assert data.updates["29852"]["positioning_time_sec"] == 80.5  # ms -> sec
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_nasku_importer.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/import_/nasku_importer.py`:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import TextIO, BinaryIO
import pandas as pd

from src.import_.csv_parser import parse_csv, validate_required_columns


REQUIRED_COLUMNS = [
    "name", "processedAt", "positioningTime", "hammeringTime",
    "hammeringStatus", "hammeringFlag"
]


class UnmatchedUpnError(Exception):
    def __init__(self, unmatched: set[str]):
        self.unmatched_upns = unmatched
        super().__init__(
            f"Nasku contains UPNs not found in drivelog: {', '.join(sorted(unmatched))}"
        )


@dataclass
class NaskuData:
    updates: dict[str, dict]  # upn -> update dict

    @classmethod
    def from_csv(cls, file: TextIO | BinaryIO) -> "NaskuData":
        df = parse_nasku(file)
        return cls(updates=extract_pile_updates(df))


def parse_nasku(file: TextIO | BinaryIO) -> pd.DataFrame:
    df = parse_csv(file)
    validate_required_columns(df, REQUIRED_COLUMNS)
    return df


def validate_upns_exist(nasku_upns: set[str], existing_upns: set[str]) -> None:
    unmatched = nasku_upns - existing_upns
    if unmatched:
        raise UnmatchedUpnError(unmatched)


def _parse_timestamp(ts_str: str) -> datetime | None:
    if pd.isna(ts_str) or ts_str == "null":
        return None
    # Handle timezone format like "2026-01-16T13:07:21.722-06:00[America/Chicago]"
    # Strip the bracketed timezone name
    if "[" in ts_str:
        ts_str = ts_str.split("[")[0]
    return datetime.fromisoformat(ts_str)


def _parse_time_ms(value) -> float | None:
    if pd.isna(value) or value == "null":
        return None
    # Convert milliseconds to seconds
    return float(value) / 1000.0


def extract_pile_updates(df: pd.DataFrame) -> dict[str, dict]:
    updates = {}
    for _, row in df.iterrows():
        upn = str(row["name"])
        updates[upn] = {
            "hammering_status": row["hammeringStatus"] if pd.notna(row["hammeringStatus"]) else None,
            "hammering_flag": row["hammeringFlag"] if pd.notna(row["hammeringFlag"]) else None,
            "hammering_time_sec": _parse_time_ms(row["hammeringTime"]),
            "positioning_time_sec": _parse_time_ms(row["positioningTime"]),
            "driven_at": _parse_timestamp(row["processedAt"]),
        }
    return updates
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_nasku_importer.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/import_/nasku_importer.py tests/test_nasku_importer.py
git commit -m "feat: add nasku CSV importer

- Extracts pile status updates from nasku format
- Validates all UPNs exist in drivelog before import
- Converts times from ms to seconds
- Parses ISO timestamps with timezone handling"
```

---

## Task 5: Progress and ETA Calculation Service

**Files:**
- Create: `src/services/__init__.py`
- Create: `src/services/progress.py`
- Create: `tests/test_progress.py`

**Step 1: Write failing tests**

Create `tests/test_progress.py`:

```python
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.data.models import Pile, Inverter, Project
from src.services.progress import (
    calculate_progress,
    calculate_pile_rate,
    calculate_eta,
    ProgressStats,
)


@pytest.fixture
def project():
    return Project(
        id=uuid4(),
        name="Test",
        default_scan_threshold_pct=90,
        default_pile_rate=50,
        created_at=datetime.now(),
    )


@pytest.fixture
def inverter(project):
    return Inverter(
        id=uuid4(),
        project_id=project.id,
        name="Inverter 1",
        total_piles=100,
        milestone_thresholds=[50, 75, 90],
        created_at=datetime.now(),
    )


def make_pile(inverter_id, upn, installed=True, driven_at=None, hammering_sec=100, positioning_sec=50):
    return Pile(
        id=uuid4(),
        inverter_id=inverter_id,
        upn=upn,
        hammering_status="COMPLETED" if installed else "INCOMPLETE",
        hammering_flag="GOOD" if installed else "UNSET",
        hammering_time_sec=hammering_sec if installed else None,
        positioning_time_sec=positioning_sec if installed else None,
        driven_at=driven_at or (datetime.now() if installed else None),
    )


class TestCalculateProgress:
    def test_returns_zero_for_no_piles(self, inverter):
        stats = calculate_progress(inverter, [])
        assert stats.installed_count == 0
        assert stats.total_count == 100
        assert stats.percentage == 0.0

    def test_calculates_correct_percentage(self, inverter):
        piles = [make_pile(inverter.id, str(i)) for i in range(25)]
        stats = calculate_progress(inverter, piles)
        assert stats.installed_count == 25
        assert stats.percentage == 25.0

    def test_only_counts_installed_piles(self, inverter):
        piles = [
            make_pile(inverter.id, "1", installed=True),
            make_pile(inverter.id, "2", installed=False),
            make_pile(inverter.id, "3", installed=True),
        ]
        stats = calculate_progress(inverter, piles)
        assert stats.installed_count == 2

    def test_handles_zero_total_piles(self):
        inv = Inverter(
            id=uuid4(),
            project_id=uuid4(),
            name="Empty",
            total_piles=0,
            created_at=datetime.now(),
        )
        stats = calculate_progress(inv, [])
        assert stats.percentage == 0.0


class TestCalculatePileRate:
    def test_returns_none_for_no_installed_piles(self, inverter):
        piles = [make_pile(inverter.id, "1", installed=False)]
        rate = calculate_pile_rate(piles)
        assert rate is None

    def test_calculates_rate_from_wall_clock_time(self, inverter):
        now = datetime.now()
        # 10 piles over 24 hours = 10 piles/day
        piles = [
            make_pile(inverter.id, str(i), driven_at=now - timedelta(hours=24))
            for i in range(10)
        ]
        rate = calculate_pile_rate(piles)
        assert rate is not None
        assert 9.5 <= rate <= 10.5  # Allow for timing variance


class TestCalculateEta:
    def test_uses_default_rate_for_unstarted_inverter(self, inverter, project):
        piles = []  # No piles installed
        eta = calculate_eta(inverter, piles, project.default_pile_rate)

        assert eta.is_using_default_rate is True
        assert eta.piles_per_day == 50
        # 100 piles at 50/day = 2 days
        assert eta.estimated_completion is not None

    def test_uses_actual_rate_for_active_inverter(self, inverter, project):
        now = datetime.now()
        # 50 piles over 24 hours = 50 piles/day
        piles = [
            make_pile(inverter.id, str(i), driven_at=now - timedelta(hours=24))
            for i in range(50)
        ]
        eta = calculate_eta(inverter, piles, project.default_pile_rate)

        assert eta.is_using_default_rate is False
        assert 49 <= eta.piles_per_day <= 51

    def test_returns_none_completion_when_done(self, inverter, project):
        # All piles installed
        piles = [make_pile(inverter.id, str(i)) for i in range(100)]
        inverter.total_piles = 100
        eta = calculate_eta(inverter, piles, project.default_pile_rate)

        # When complete, ETA should indicate completion
        assert eta.remaining_piles == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_progress.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `src/services/__init__.py` (empty) and `src/services/progress.py`:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.data.models import Inverter, Pile


@dataclass
class ProgressStats:
    installed_count: int
    total_count: int
    percentage: float


@dataclass
class EtaStats:
    remaining_piles: int
    piles_per_day: float
    is_using_default_rate: bool
    estimated_completion: datetime | None


def calculate_progress(inverter: Inverter, piles: list[Pile]) -> ProgressStats:
    installed = sum(1 for p in piles if p.is_installed)
    total = inverter.total_piles

    if total == 0:
        percentage = 0.0
    else:
        percentage = (installed / total) * 100

    return ProgressStats(
        installed_count=installed,
        total_count=total,
        percentage=percentage,
    )


def calculate_pile_rate(piles: list[Pile]) -> float | None:
    installed_piles = [p for p in piles if p.is_installed and p.driven_at]

    if not installed_piles:
        return None

    # Find earliest driven_at
    earliest = min(p.driven_at for p in installed_piles)
    now = datetime.now()

    # Calculate days elapsed
    elapsed = now - earliest
    days = elapsed.total_seconds() / (24 * 60 * 60)

    if days < 0.001:  # Avoid division by very small numbers
        return None

    return len(installed_piles) / days


def calculate_eta(
    inverter: Inverter,
    piles: list[Pile],
    default_rate: int,
) -> EtaStats:
    progress = calculate_progress(inverter, piles)
    remaining = inverter.total_piles - progress.installed_count

    if remaining <= 0:
        return EtaStats(
            remaining_piles=0,
            piles_per_day=0.0,
            is_using_default_rate=False,
            estimated_completion=None,
        )

    actual_rate = calculate_pile_rate(piles)

    if actual_rate is not None:
        rate = actual_rate
        using_default = False
    else:
        rate = float(default_rate)
        using_default = True

    if rate > 0:
        days_remaining = remaining / rate
        completion = datetime.now() + timedelta(days=days_remaining)
    else:
        completion = None

    return EtaStats(
        remaining_piles=remaining,
        piles_per_day=rate,
        is_using_default_rate=using_default,
        estimated_completion=completion,
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_progress.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/services/ tests/test_progress.py
git commit -m "feat: add progress and ETA calculation service

- calculate_progress: installed count and percentage
- calculate_pile_rate: wall-clock based piles/day
- calculate_eta: completion estimate with default rate fallback"
```

---

## Task 6: Alert Service

**Files:**
- Create: `src/services/alerts.py`
- Create: `tests/test_alerts.py`

**Step 1: Write failing tests**

Create `tests/test_alerts.py`:

```python
import pytest
from datetime import datetime
from uuid import uuid4

from src.data.models import Inverter, Alert
from src.services.alerts import (
    check_milestone_alerts,
    get_pending_alerts,
    AlertCheck,
)


@pytest.fixture
def inverter():
    return Inverter(
        id=uuid4(),
        project_id=uuid4(),
        name="Inverter 1",
        total_piles=100,
        milestone_thresholds=[50, 75, 90],
        created_at=datetime.now(),
    )


class TestCheckMilestoneAlerts:
    def test_returns_crossed_milestones(self, inverter):
        # Progress went from 0% to 60%
        result = check_milestone_alerts(
            inverter=inverter,
            previous_percentage=0.0,
            current_percentage=60.0,
        )
        assert len(result) == 1
        assert result[0].threshold == 50

    def test_returns_multiple_crossed_milestones(self, inverter):
        # Progress went from 0% to 80%
        result = check_milestone_alerts(
            inverter=inverter,
            previous_percentage=0.0,
            current_percentage=80.0,
        )
        assert len(result) == 2
        thresholds = {r.threshold for r in result}
        assert thresholds == {50, 75}

    def test_returns_empty_when_no_milestones_crossed(self, inverter):
        result = check_milestone_alerts(
            inverter=inverter,
            previous_percentage=51.0,
            current_percentage=55.0,
        )
        assert result == []

    def test_ignores_already_passed_milestones(self, inverter):
        # Progress from 55% to 80% should only trigger 75%
        result = check_milestone_alerts(
            inverter=inverter,
            previous_percentage=55.0,
            current_percentage=80.0,
        )
        assert len(result) == 1
        assert result[0].threshold == 75


class TestGetPendingAlerts:
    def test_filters_unacknowledged_alerts(self, inverter):
        alerts = [
            Alert(
                id=uuid4(),
                inverter_id=inverter.id,
                alert_type="milestone_reached",
                threshold_value=50,
                acknowledged=False,
                created_at=datetime.now(),
            ),
            Alert(
                id=uuid4(),
                inverter_id=inverter.id,
                alert_type="milestone_reached",
                threshold_value=75,
                acknowledged=True,
                created_at=datetime.now(),
            ),
        ]
        pending = get_pending_alerts(alerts)
        assert len(pending) == 1
        assert pending[0].threshold_value == 50
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_alerts.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `src/services/alerts.py`:

```python
from dataclasses import dataclass

from src.data.models import Inverter, Alert


@dataclass
class AlertCheck:
    inverter_id: str
    threshold: int
    alert_type: str = "milestone_reached"


def check_milestone_alerts(
    inverter: Inverter,
    previous_percentage: float,
    current_percentage: float,
) -> list[AlertCheck]:
    crossed = []

    for threshold in inverter.milestone_thresholds:
        # Milestone is crossed if we went from below to at-or-above
        if previous_percentage < threshold <= current_percentage:
            crossed.append(AlertCheck(
                inverter_id=str(inverter.id),
                threshold=threshold,
            ))

    return crossed


def get_pending_alerts(alerts: list[Alert]) -> list[Alert]:
    return [a for a in alerts if not a.acknowledged]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_alerts.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/services/alerts.py tests/test_alerts.py
git commit -m "feat: add alert service for milestone notifications

- check_milestone_alerts: detects newly crossed thresholds
- get_pending_alerts: filters unacknowledged alerts"
```

---

## Task 7: Repository Interface and Supabase Implementation

**Files:**
- Create: `src/data/repository.py`
- Create: `src/data/supabase_repo.py`
- Create: `tests/test_repository.py`

**Step 1: Write failing tests for repository interface**

Create `tests/test_repository.py`:

```python
import pytest
from abc import ABC
from uuid import uuid4
from datetime import datetime

from src.data.repository import Repository
from src.data.models import Project, Inverter, Pile, WorkflowStep, Alert


class TestRepositoryInterface:
    def test_repository_is_abstract(self):
        assert issubclass(Repository, ABC)

    def test_repository_has_project_methods(self):
        assert hasattr(Repository, "get_project")
        assert hasattr(Repository, "save_project")
        assert hasattr(Repository, "update_project")

    def test_repository_has_inverter_methods(self):
        assert hasattr(Repository, "get_inverters")
        assert hasattr(Repository, "get_inverter")
        assert hasattr(Repository, "save_inverter")
        assert hasattr(Repository, "update_inverter")

    def test_repository_has_pile_methods(self):
        assert hasattr(Repository, "get_piles_for_inverter")
        assert hasattr(Repository, "save_piles")
        assert hasattr(Repository, "update_pile")

    def test_repository_has_workflow_methods(self):
        assert hasattr(Repository, "get_workflow_steps")
        assert hasattr(Repository, "save_workflow_steps")
        assert hasattr(Repository, "update_workflow_step")

    def test_repository_has_alert_methods(self):
        assert hasattr(Repository, "get_alerts_for_inverter")
        assert hasattr(Repository, "save_alert")
        assert hasattr(Repository, "acknowledge_alert")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_repository.py -v`
Expected: FAIL

**Step 3: Write repository interface**

Create `src/data/repository.py`:

```python
from abc import ABC, abstractmethod
from uuid import UUID

from src.data.models import Project, Inverter, Pile, WorkflowStep, Alert


class Repository(ABC):
    # Project methods
    @abstractmethod
    def get_project(self) -> Project | None:
        pass

    @abstractmethod
    def save_project(self, project: Project) -> Project:
        pass

    @abstractmethod
    def update_project(self, project: Project) -> Project:
        pass

    # Inverter methods
    @abstractmethod
    def get_inverters(self, project_id: UUID) -> list[Inverter]:
        pass

    @abstractmethod
    def get_inverter(self, inverter_id: UUID) -> Inverter | None:
        pass

    @abstractmethod
    def save_inverter(self, inverter: Inverter) -> Inverter:
        pass

    @abstractmethod
    def update_inverter(self, inverter: Inverter) -> Inverter:
        pass

    # Pile methods
    @abstractmethod
    def get_piles_for_inverter(self, inverter_id: UUID) -> list[Pile]:
        pass

    @abstractmethod
    def save_piles(self, piles: list[Pile]) -> list[Pile]:
        pass

    @abstractmethod
    def update_pile(self, pile: Pile) -> Pile:
        pass

    @abstractmethod
    def get_pile_by_upn(self, inverter_id: UUID, upn: str) -> Pile | None:
        pass

    # Workflow methods
    @abstractmethod
    def get_workflow_steps(self, inverter_id: UUID) -> list[WorkflowStep]:
        pass

    @abstractmethod
    def save_workflow_steps(self, steps: list[WorkflowStep]) -> list[WorkflowStep]:
        pass

    @abstractmethod
    def update_workflow_step(self, step: WorkflowStep) -> WorkflowStep:
        pass

    # Alert methods
    @abstractmethod
    def get_alerts_for_inverter(self, inverter_id: UUID) -> list[Alert]:
        pass

    @abstractmethod
    def save_alert(self, alert: Alert) -> Alert:
        pass

    @abstractmethod
    def acknowledge_alert(self, alert_id: UUID) -> Alert:
        pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_repository.py -v`
Expected: PASS

**Step 5: Create Supabase implementation skeleton**

Create `src/data/supabase_repo.py`:

```python
import os
from uuid import UUID

from supabase import create_client, Client

from src.data.repository import Repository
from src.data.models import Project, Inverter, Pile, WorkflowStep, Alert


class SupabaseRepository(Repository):
    def __init__(self, url: str | None = None, key: str | None = None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.client: Client = create_client(self.url, self.key)

    def get_project(self) -> Project | None:
        result = self.client.table("projects").select("*").limit(1).execute()
        if not result.data:
            return None
        return Project(**result.data[0])

    def save_project(self, project: Project) -> Project:
        data = project.model_dump(mode="json")
        result = self.client.table("projects").insert(data).execute()
        return Project(**result.data[0])

    def update_project(self, project: Project) -> Project:
        data = project.model_dump(mode="json")
        result = (
            self.client.table("projects")
            .update(data)
            .eq("id", str(project.id))
            .execute()
        )
        return Project(**result.data[0])

    def get_inverters(self, project_id: UUID) -> list[Inverter]:
        result = (
            self.client.table("inverters")
            .select("*")
            .eq("project_id", str(project_id))
            .execute()
        )
        return [Inverter(**row) for row in result.data]

    def get_inverter(self, inverter_id: UUID) -> Inverter | None:
        result = (
            self.client.table("inverters")
            .select("*")
            .eq("id", str(inverter_id))
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return Inverter(**result.data[0])

    def save_inverter(self, inverter: Inverter) -> Inverter:
        data = inverter.model_dump(mode="json")
        result = self.client.table("inverters").insert(data).execute()
        return Inverter(**result.data[0])

    def update_inverter(self, inverter: Inverter) -> Inverter:
        data = inverter.model_dump(mode="json")
        result = (
            self.client.table("inverters")
            .update(data)
            .eq("id", str(inverter.id))
            .execute()
        )
        return Inverter(**result.data[0])

    def get_piles_for_inverter(self, inverter_id: UUID) -> list[Pile]:
        result = (
            self.client.table("piles")
            .select("*")
            .eq("inverter_id", str(inverter_id))
            .execute()
        )
        return [Pile(**row) for row in result.data]

    def save_piles(self, piles: list[Pile]) -> list[Pile]:
        data = [p.model_dump(mode="json") for p in piles]
        result = self.client.table("piles").insert(data).execute()
        return [Pile(**row) for row in result.data]

    def update_pile(self, pile: Pile) -> Pile:
        data = pile.model_dump(mode="json")
        result = (
            self.client.table("piles")
            .update(data)
            .eq("id", str(pile.id))
            .execute()
        )
        return Pile(**result.data[0])

    def get_pile_by_upn(self, inverter_id: UUID, upn: str) -> Pile | None:
        result = (
            self.client.table("piles")
            .select("*")
            .eq("inverter_id", str(inverter_id))
            .eq("upn", upn)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return Pile(**result.data[0])

    def get_workflow_steps(self, inverter_id: UUID) -> list[WorkflowStep]:
        result = (
            self.client.table("workflow_steps")
            .select("*")
            .eq("inverter_id", str(inverter_id))
            .order("step_order")
            .execute()
        )
        return [WorkflowStep(**row) for row in result.data]

    def save_workflow_steps(self, steps: list[WorkflowStep]) -> list[WorkflowStep]:
        data = [s.model_dump(mode="json") for s in steps]
        result = self.client.table("workflow_steps").insert(data).execute()
        return [WorkflowStep(**row) for row in result.data]

    def update_workflow_step(self, step: WorkflowStep) -> WorkflowStep:
        data = step.model_dump(mode="json")
        result = (
            self.client.table("workflow_steps")
            .update(data)
            .eq("id", str(step.id))
            .execute()
        )
        return WorkflowStep(**result.data[0])

    def get_alerts_for_inverter(self, inverter_id: UUID) -> list[Alert]:
        result = (
            self.client.table("alerts")
            .select("*")
            .eq("inverter_id", str(inverter_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [Alert(**row) for row in result.data]

    def save_alert(self, alert: Alert) -> Alert:
        data = alert.model_dump(mode="json")
        result = self.client.table("alerts").insert(data).execute()
        return Alert(**result.data[0])

    def acknowledge_alert(self, alert_id: UUID) -> Alert:
        result = (
            self.client.table("alerts")
            .update({"acknowledged": True})
            .eq("id", str(alert_id))
            .execute()
        )
        return Alert(**result.data[0])
```

**Step 6: Commit**

```bash
git add src/data/repository.py src/data/supabase_repo.py tests/test_repository.py
git commit -m "feat: add repository interface and Supabase implementation

- Abstract Repository base class for data layer
- SupabaseRepository with full CRUD for all entities
- Enables future database swapping"
```

---

## Task 8: Workflow Step Constants and Factory

**Files:**
- Modify: `src/data/models.py`
- Create: `src/data/workflow.py`
- Create: `tests/test_workflow.py`

**Step 1: Write failing test**

Create `tests/test_workflow.py`:

```python
import pytest
from uuid import uuid4

from src.data.workflow import WORKFLOW_STEPS, create_workflow_steps


class TestWorkflowSteps:
    def test_has_eleven_steps(self):
        assert len(WORKFLOW_STEPS) == 11

    def test_steps_are_ordered(self):
        for i, step in enumerate(WORKFLOW_STEPS, start=1):
            assert step["order"] == i

    def test_first_step_is_first_scan(self):
        assert WORKFLOW_STEPS[0]["name"] == "First Scan"

    def test_last_step_is_walk_down(self):
        assert WORKFLOW_STEPS[-1]["name"] == "Walk Down"


class TestCreateWorkflowSteps:
    def test_creates_eleven_steps_for_inverter(self):
        inverter_id = uuid4()
        steps = create_workflow_steps(inverter_id)

        assert len(steps) == 11
        for step in steps:
            assert step.inverter_id == inverter_id
            assert step.is_complete is False

    def test_steps_have_correct_order(self):
        steps = create_workflow_steps(uuid4())
        orders = [s.step_order for s in steps]
        assert orders == list(range(1, 12))

    def test_each_step_has_unique_id(self):
        steps = create_workflow_steps(uuid4())
        ids = [s.id for s in steps]
        assert len(ids) == len(set(ids))
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_workflow.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `src/data/workflow.py`:

```python
from uuid import uuid4, UUID

from src.data.models import WorkflowStep


WORKFLOW_STEPS = [
    {"order": 1, "name": "First Scan"},
    {"order": 2, "name": "Processed"},
    {"order": 3, "name": "Points Picked"},
    {"order": 4, "name": "Pushed to ArcGIS"},
    {"order": 5, "name": "Remediation Performed"},
    {"order": 6, "name": "Second Scan Complete"},
    {"order": 7, "name": "Processed"},
    {"order": 8, "name": "Points Picked"},
    {"order": 9, "name": "Pushed to ArcGIS"},
    {"order": 10, "name": "Second Remediation Performed"},
    {"order": 11, "name": "Walk Down"},
]


def create_workflow_steps(inverter_id: UUID) -> list[WorkflowStep]:
    return [
        WorkflowStep(
            id=uuid4(),
            inverter_id=inverter_id,
            step_name=step["name"],
            step_order=step["order"],
            is_complete=False,
            completed_at=None,
            due_date=None,
            assigned_engineer=None,
        )
        for step in WORKFLOW_STEPS
    ]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_workflow.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/data/workflow.py tests/test_workflow.py
git commit -m "feat: add workflow step constants and factory

- 11 workflow steps defined as constants
- create_workflow_steps factory for new inverters"
```

---

## Task 9: Import Orchestration Service

**Files:**
- Create: `src/services/import_service.py`
- Create: `tests/test_import_service.py`

**Step 1: Write failing tests**

Create `tests/test_import_service.py`:

```python
import pytest
from io import StringIO
from uuid import uuid4
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.services.import_service import ImportService
from src.data.models import Project, Inverter, Pile
from src.import_.nasku_importer import UnmatchedUpnError


SAMPLE_DRIVELOG = """Inverter,UPN,Hammering_Status,Hammering_Flag
1,12345,COMPLETED,GOOD
1,12346,COMPLETED,GOOD
2,22222,INCOMPLETE,UNSET
"""

SAMPLE_NASKU = """name,processedAt,positioningTime,hammeringTime,hammeringStatus,hammeringFlag
12345,2026-01-16T13:07:21.722-06:00,80000,17870,COMPLETED,GOOD
12346,2026-01-16T14:00:00.000-06:00,90000,20000,COMPLETED,GOOD
"""


@pytest.fixture
def mock_repo():
    repo = Mock()
    repo.get_project.return_value = None
    repo.save_project.side_effect = lambda p: p
    repo.save_inverter.side_effect = lambda i: i
    repo.save_piles.side_effect = lambda piles: piles
    repo.save_workflow_steps.side_effect = lambda steps: steps
    return repo


class TestImportDrivelog:
    def test_creates_project_and_inverters(self, mock_repo):
        service = ImportService(mock_repo)
        result = service.import_drivelog(
            StringIO(SAMPLE_DRIVELOG),
            project_name="Test Project",
        )

        assert mock_repo.save_project.called
        assert mock_repo.save_inverter.call_count == 2  # Two inverters

    def test_creates_piles_for_each_inverter(self, mock_repo):
        service = ImportService(mock_repo)
        service.import_drivelog(StringIO(SAMPLE_DRIVELOG), "Test")

        # Should save piles (called once per inverter or once with all)
        assert mock_repo.save_piles.called

    def test_creates_workflow_steps_for_each_inverter(self, mock_repo):
        service = ImportService(mock_repo)
        service.import_drivelog(StringIO(SAMPLE_DRIVELOG), "Test")

        # 11 steps per inverter, 2 inverters
        assert mock_repo.save_workflow_steps.called


class TestImportNasku:
    def test_updates_existing_piles(self, mock_repo):
        # Setup existing piles
        existing_pile = Pile(
            id=uuid4(),
            inverter_id=uuid4(),
            upn="12345",
            hammering_status=None,
            hammering_flag=None,
        )
        mock_repo.get_pile_by_upn.return_value = existing_pile
        mock_repo.update_pile.side_effect = lambda p: p
        mock_repo.get_inverters.return_value = [
            Inverter(
                id=existing_pile.inverter_id,
                project_id=uuid4(),
                name="1",
                total_piles=2,
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

        service = ImportService(mock_repo)
        service.import_nasku(StringIO(SAMPLE_NASKU))

        assert mock_repo.update_pile.called

    def test_rejects_import_when_upn_not_found(self, mock_repo):
        mock_repo.get_pile_by_upn.return_value = None
        mock_repo.get_project.return_value = Project(
            id=uuid4(),
            name="Test",
            default_scan_threshold_pct=90,
            default_pile_rate=50,
            created_at=datetime.now(),
        )
        mock_repo.get_inverters.return_value = []

        service = ImportService(mock_repo)
        with pytest.raises(UnmatchedUpnError):
            service.import_nasku(StringIO(SAMPLE_NASKU))
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_import_service.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

Create `src/services/import_service.py`:

```python
from datetime import datetime
from typing import TextIO, BinaryIO
from uuid import uuid4, UUID

from src.data.repository import Repository
from src.data.models import Project, Inverter, Pile
from src.data.workflow import create_workflow_steps
from src.import_.drivelog_importer import DrivelogData
from src.import_.nasku_importer import NaskuData, validate_upns_exist, UnmatchedUpnError
from src.services.alerts import check_milestone_alerts
from src.services.progress import calculate_progress


class ImportService:
    def __init__(self, repository: Repository):
        self.repo = repository

    def import_drivelog(
        self,
        file: TextIO | BinaryIO,
        project_name: str,
    ) -> Project:
        data = DrivelogData.from_csv(file)

        # Create project
        project = Project(
            id=uuid4(),
            name=project_name,
            default_scan_threshold_pct=90,
            default_pile_rate=50,
            created_at=datetime.now(),
        )
        project = self.repo.save_project(project)

        # Create inverters, piles, and workflow steps
        for inverter_name, pile_count in data.inverters.items():
            inverter = Inverter(
                id=uuid4(),
                project_id=project.id,
                name=inverter_name,
                total_piles=pile_count,
                milestone_thresholds=[50, 75, 90],
                created_at=datetime.now(),
            )
            inverter = self.repo.save_inverter(inverter)

            # Create piles
            pile_data = data.piles.get(inverter_name, [])
            piles = [
                Pile(
                    id=uuid4(),
                    inverter_id=inverter.id,
                    upn=p["upn"],
                    hammering_status=p["hammering_status"],
                    hammering_flag=p["hammering_flag"],
                )
                for p in pile_data
            ]
            if piles:
                self.repo.save_piles(piles)

            # Create workflow steps
            steps = create_workflow_steps(inverter.id)
            self.repo.save_workflow_steps(steps)

        return project

    def import_nasku(self, file: TextIO | BinaryIO) -> None:
        project = self.repo.get_project()
        if not project:
            raise ValueError("No project exists. Import drivelog first.")

        data = NaskuData.from_csv(file)

        # Collect all existing UPNs across all inverters
        inverters = self.repo.get_inverters(project.id)
        existing_upns: set[str] = set()
        upn_to_inverter: dict[str, UUID] = {}

        for inverter in inverters:
            piles = self.repo.get_piles_for_inverter(inverter.id)
            for pile in piles:
                existing_upns.add(pile.upn)
                upn_to_inverter[pile.upn] = inverter.id

        # Validate all UPNs exist
        nasku_upns = set(data.updates.keys())
        validate_upns_exist(nasku_upns, existing_upns)

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
                self.repo.update_pile(pile)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_import_service.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/services/import_service.py tests/test_import_service.py
git commit -m "feat: add import orchestration service

- import_drivelog: creates project, inverters, piles, workflow steps
- import_nasku: validates UPNs and updates pile status
- Rejects nasku import if any UPN not found"
```

---

## Task 10: Supabase Database Setup Script

**Files:**
- Create: `scripts/setup_database.sql`

**Step 1: Create SQL migration script**

Create `scripts/setup_database.sql`:

```sql
-- Inverter Tracker Dashboard - Supabase Schema
-- Run this in the Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    default_scan_threshold_pct INTEGER NOT NULL DEFAULT 90,
    default_pile_rate INTEGER NOT NULL DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inverters table
CREATE TABLE inverters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    total_piles INTEGER NOT NULL,
    scan_threshold_override INTEGER,
    milestone_thresholds JSONB DEFAULT '[50, 75, 90]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_inverters_project ON inverters(project_id);

-- Piles table
CREATE TABLE piles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inverter_id UUID NOT NULL REFERENCES inverters(id) ON DELETE CASCADE,
    upn TEXT NOT NULL,
    hammering_status TEXT,
    hammering_flag TEXT,
    hammering_time_sec DOUBLE PRECISION,
    positioning_time_sec DOUBLE PRECISION,
    driven_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(inverter_id, upn)
);

CREATE INDEX idx_piles_inverter ON piles(inverter_id);
CREATE INDEX idx_piles_upn ON piles(upn);

-- Workflow steps table
CREATE TABLE workflow_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inverter_id UUID NOT NULL REFERENCES inverters(id) ON DELETE CASCADE,
    step_name TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    is_complete BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    due_date DATE,
    assigned_engineer TEXT
);

CREATE INDEX idx_workflow_inverter ON workflow_steps(inverter_id);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inverter_id UUID NOT NULL REFERENCES inverters(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL,
    threshold_value INTEGER NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_alerts_inverter ON alerts(inverter_id);
CREATE INDEX idx_alerts_unacknowledged ON alerts(inverter_id) WHERE acknowledged = FALSE;

-- Row Level Security (disabled for v1 - no auth)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE inverters ENABLE ROW LEVEL SECURITY;
ALTER TABLE piles ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Allow all operations for anon key (v1 - no auth)
CREATE POLICY "Allow all" ON projects FOR ALL USING (true);
CREATE POLICY "Allow all" ON inverters FOR ALL USING (true);
CREATE POLICY "Allow all" ON piles FOR ALL USING (true);
CREATE POLICY "Allow all" ON workflow_steps FOR ALL USING (true);
CREATE POLICY "Allow all" ON alerts FOR ALL USING (true);
```

**Step 2: Commit**

```bash
git add scripts/setup_database.sql
git commit -m "feat: add Supabase database schema

- All 5 tables with proper indexes
- Foreign key relationships with CASCADE delete
- RLS enabled but permissive for v1 (no auth)"
```

---

## Task 11: Streamlit UI - Dashboard Grid

**Files:**
- Create: `src/ui/__init__.py`
- Create: `src/ui/dashboard.py`
- Create: `src/ui/state.py`
- Create: `src/app.py`

**Step 1: Create state management**

Create `src/ui/__init__.py` (empty) and `src/ui/state.py`:

```python
import streamlit as st
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.data.repository import Repository


def init_session_state():
    if "selected_inverter_id" not in st.session_state:
        st.session_state.selected_inverter_id = None
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False


def get_repository() -> "Repository":
    from src.data.supabase_repo import SupabaseRepository

    if "repository" not in st.session_state:
        st.session_state.repository = SupabaseRepository()
    return st.session_state.repository
```

**Step 2: Create dashboard grid**

Create `src/ui/dashboard.py`:

```python
import streamlit as st
from datetime import date, timedelta

from src.data.models import Inverter, WorkflowStep
from src.services.progress import calculate_progress, calculate_eta, ProgressStats, EtaStats
from src.services.alerts import get_pending_alerts
from src.ui.state import get_repository


def get_status_color(step: WorkflowStep | None, days_remaining: int | None) -> str:
    if step is None or step.due_date is None:
        return "green"

    if days_remaining is None:
        return "green"
    elif days_remaining < 2:
        return "red"
    elif days_remaining <= 6:
        return "yellow"
    else:
        return "green"


def get_current_step(steps: list[WorkflowStep]) -> WorkflowStep | None:
    for step in sorted(steps, key=lambda s: s.step_order):
        if not step.is_complete:
            return step
    return None


def days_until_due(step: WorkflowStep | None) -> int | None:
    if step is None or step.due_date is None:
        return None
    return (step.due_date - date.today()).days


def render_inverter_card(
    inverter: Inverter,
    progress: ProgressStats,
    eta: EtaStats,
    current_step: WorkflowStep | None,
    has_pending_alerts: bool,
):
    days_remaining = days_until_due(current_step)
    color = get_status_color(current_step, days_remaining)

    color_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[color]

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(inverter.name)

        with col2:
            if has_pending_alerts:
                st.markdown("**[!]**")

        # Progress bar
        st.progress(progress.percentage / 100)
        st.caption(f"{progress.percentage:.0f}% ({progress.installed_count}/{progress.total_count})")

        # Current step
        step_name = current_step.step_name if current_step else "Complete"
        st.markdown(f"**{step_name}**")

        # Status and engineer
        if current_step:
            due_text = ""
            if days_remaining is not None:
                if days_remaining < 0:
                    due_text = f"Overdue by {abs(days_remaining)}d"
                elif days_remaining == 0:
                    due_text = "Due today"
                else:
                    due_text = f"Due: {days_remaining}d"

            engineer = current_step.assigned_engineer or "--"
            st.caption(f"{color_emoji} {due_text} | @{engineer}")

        # ETA
        if eta.estimated_completion:
            eta_str = eta.estimated_completion.strftime("%b %d")
            rate_note = " (default)" if eta.is_using_default_rate else ""
            st.caption(f"ETA: {eta_str} | {eta.piles_per_day:.0f} piles/d{rate_note}")

        # Click to expand
        if st.button("Details", key=f"expand_{inverter.id}"):
            st.session_state.selected_inverter_id = str(inverter.id)
            st.rerun()


def render_dashboard():
    repo = get_repository()
    project = repo.get_project()

    if not project:
        st.warning("No project loaded. Please import a drivelog CSV to get started.")
        return

    st.title(f"Project: {project.name}")

    # Header buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("Import CSV"):
            st.session_state.show_import = True
    with col2:
        if st.button("Settings"):
            st.session_state.show_settings = True

    st.divider()

    # Get all inverters
    inverters = repo.get_inverters(project.id)

    if not inverters:
        st.info("No inverters found. Import a drivelog to add inverters.")
        return

    # Render grid of cards (3 columns)
    cols = st.columns(3)

    for i, inverter in enumerate(sorted(inverters, key=lambda x: x.name)):
        with cols[i % 3]:
            # Get data for this inverter
            piles = repo.get_piles_for_inverter(inverter.id)
            steps = repo.get_workflow_steps(inverter.id)
            alerts = repo.get_alerts_for_inverter(inverter.id)

            progress = calculate_progress(inverter, piles)
            eta = calculate_eta(inverter, piles, project.default_pile_rate)
            current_step = get_current_step(steps)
            pending = get_pending_alerts(alerts)

            render_inverter_card(
                inverter=inverter,
                progress=progress,
                eta=eta,
                current_step=current_step,
                has_pending_alerts=len(pending) > 0,
            )
```

**Step 3: Create main app entry**

Create `src/app.py`:

```python
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.ui.state import init_session_state
from src.ui.dashboard import render_dashboard


st.set_page_config(
    page_title="Inverter Tracker",
    page_icon="⚡",
    layout="wide",
)


def main():
    init_session_state()

    # Check if we should show expanded card
    if st.session_state.get("selected_inverter_id"):
        from src.ui.expanded_card import render_expanded_card
        render_expanded_card(st.session_state.selected_inverter_id)
    elif st.session_state.get("show_settings"):
        from src.ui.settings import render_settings
        render_settings()
    elif st.session_state.get("show_import"):
        from src.ui.import_panel import render_import_panel
        render_import_panel()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
```

**Step 4: Commit**

```bash
git add src/app.py src/ui/
git commit -m "feat: add Streamlit dashboard with inverter card grid

- Main dashboard with 3-column card layout
- Progress bar, current step, ETA display
- Color-coded status based on due dates
- Session state management"
```

---

## Task 12: Streamlit UI - Expanded Card with Workflow

**Files:**
- Create: `src/ui/expanded_card.py`

**Step 1: Create expanded card component**

Create `src/ui/expanded_card.py`:

```python
import streamlit as st
from datetime import date
from uuid import UUID

from src.ui.state import get_repository
from src.services.progress import calculate_progress, calculate_eta
from src.services.alerts import get_pending_alerts


def render_expanded_card(inverter_id: str):
    repo = get_repository()
    project = repo.get_project()
    inverter = repo.get_inverter(UUID(inverter_id))

    if not inverter or not project:
        st.error("Inverter not found")
        return

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.selected_inverter_id = None
        st.rerun()

    st.title(inverter.name)

    # Get data
    piles = repo.get_piles_for_inverter(inverter.id)
    steps = repo.get_workflow_steps(inverter.id)
    alerts = repo.get_alerts_for_inverter(inverter.id)

    progress = calculate_progress(inverter, piles)
    eta = calculate_eta(inverter, piles, project.default_pile_rate)
    pending_alerts = get_pending_alerts(alerts)

    # Progress summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Progress", f"{progress.percentage:.1f}%")
    with col2:
        st.metric("Piles", f"{progress.installed_count}/{progress.total_count}")
    with col3:
        if eta.estimated_completion:
            st.metric("ETA", eta.estimated_completion.strftime("%b %d, %Y"))
        else:
            st.metric("ETA", "Complete" if progress.percentage == 100 else "N/A")

    st.divider()

    # Alerts section
    if pending_alerts:
        st.subheader("Pending Alerts")
        for alert in pending_alerts:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.warning(f"Milestone reached: {alert.threshold_value}%")
            with col2:
                if st.button("Acknowledge", key=f"ack_{alert.id}"):
                    repo.acknowledge_alert(alert.id)
                    st.rerun()
        st.divider()

    # Workflow checklist
    st.subheader("Workflow Steps")

    # Get list of engineers for dropdown
    engineers = ["", "Sarah", "John", "Mike", "Lisa"]  # TODO: Load from project settings

    for step in sorted(steps, key=lambda s: s.step_order):
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([0.5, 2, 1.5, 1.5])

            with col1:
                new_complete = st.checkbox(
                    "",
                    value=step.is_complete,
                    key=f"step_{step.id}",
                    label_visibility="collapsed",
                )
                if new_complete != step.is_complete:
                    step.is_complete = new_complete
                    step.completed_at = date.today() if new_complete else None
                    repo.update_workflow_step(step)
                    st.rerun()

            with col2:
                st.markdown(f"**{step.step_order}. {step.step_name}**")

            with col3:
                new_due = st.date_input(
                    "Due",
                    value=step.due_date,
                    key=f"due_{step.id}",
                    label_visibility="collapsed",
                )
                if new_due != step.due_date:
                    step.due_date = new_due
                    repo.update_workflow_step(step)

            with col4:
                current_idx = engineers.index(step.assigned_engineer) if step.assigned_engineer in engineers else 0
                new_engineer = st.selectbox(
                    "Engineer",
                    options=engineers,
                    index=current_idx,
                    key=f"eng_{step.id}",
                    label_visibility="collapsed",
                )
                if new_engineer != step.assigned_engineer:
                    step.assigned_engineer = new_engineer or None
                    repo.update_workflow_step(step)

    st.divider()

    # Inverter settings
    st.subheader("Inverter Settings")

    col1, col2 = st.columns(2)

    with col1:
        new_threshold = st.number_input(
            "First Scan Threshold Override (%)",
            min_value=0,
            max_value=100,
            value=inverter.scan_threshold_override or project.default_scan_threshold_pct,
            help=f"Project default: {project.default_scan_threshold_pct}%",
        )
        use_override = st.checkbox(
            "Use custom threshold",
            value=inverter.scan_threshold_override is not None,
        )

        if use_override and new_threshold != inverter.scan_threshold_override:
            inverter.scan_threshold_override = new_threshold
            repo.update_inverter(inverter)
        elif not use_override and inverter.scan_threshold_override is not None:
            inverter.scan_threshold_override = None
            repo.update_inverter(inverter)

    with col2:
        st.text("Milestone Thresholds")
        thresholds_str = st.text_input(
            "Thresholds (comma-separated)",
            value=", ".join(str(t) for t in inverter.milestone_thresholds),
            label_visibility="collapsed",
        )
        try:
            new_thresholds = [int(t.strip()) for t in thresholds_str.split(",")]
            if new_thresholds != inverter.milestone_thresholds:
                inverter.milestone_thresholds = new_thresholds
                repo.update_inverter(inverter)
        except ValueError:
            st.error("Invalid thresholds format")
```

**Step 2: Commit**

```bash
git add src/ui/expanded_card.py
git commit -m "feat: add expanded inverter card with workflow checklist

- Full workflow step list with checkboxes
- Due date picker per step
- Engineer assignment dropdown
- Alert acknowledgment
- Inverter-level settings (threshold override, milestones)"
```

---

## Task 13: Streamlit UI - Import Panel

**Files:**
- Create: `src/ui/import_panel.py`

**Step 1: Create import panel**

Create `src/ui/import_panel.py`:

```python
import streamlit as st

from src.ui.state import get_repository
from src.services.import_service import ImportService
from src.import_.csv_parser import MissingColumnsError
from src.import_.nasku_importer import UnmatchedUpnError


def render_import_panel():
    repo = get_repository()
    project = repo.get_project()

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.show_import = False
        st.rerun()

    st.title("Import CSV Data")

    import_service = ImportService(repo)

    # Drivelog import (only if no project exists)
    if not project:
        st.subheader("Step 1: Import Drivelog")
        st.info("Import a drivelog CSV to set up your project with inverters and piles.")

        project_name = st.text_input("Project Name", value="Solar Site")
        drivelog_file = st.file_uploader(
            "Upload Drivelog CSV",
            type=["csv"],
            key="drivelog",
        )

        if drivelog_file and project_name:
            if st.button("Import Drivelog"):
                try:
                    with st.spinner("Importing drivelog..."):
                        project = import_service.import_drivelog(
                            drivelog_file,
                            project_name=project_name,
                        )
                    st.success(f"Project '{project.name}' created successfully!")
                    st.session_state.show_import = False
                    st.rerun()
                except MissingColumnsError as e:
                    st.error(f"Missing required columns: {', '.join(e.missing)}")
                except Exception as e:
                    st.error(f"Import failed: {str(e)}")

    else:
        st.subheader("Import Nasku Progress Update")
        st.info(f"Update pile status for project: **{project.name}**")

        nasku_file = st.file_uploader(
            "Upload Nasku CSV",
            type=["csv"],
            key="nasku",
        )

        if nasku_file:
            if st.button("Import Nasku"):
                try:
                    with st.spinner("Importing nasku data..."):
                        import_service.import_nasku(nasku_file)
                    st.success("Pile status updated successfully!")
                    st.session_state.show_import = False
                    st.rerun()
                except MissingColumnsError as e:
                    st.error(f"Missing required columns: {', '.join(e.missing)}")
                except UnmatchedUpnError as e:
                    st.error(f"Import rejected. UPNs not found in drivelog: {', '.join(sorted(e.unmatched_upns)[:10])}")
                    if len(e.unmatched_upns) > 10:
                        st.error(f"... and {len(e.unmatched_upns) - 10} more")
                except Exception as e:
                    st.error(f"Import failed: {str(e)}")

        st.divider()

        # Option to reset project
        with st.expander("Advanced: Reset Project"):
            st.warning("This will delete all data and allow re-importing a drivelog.")
            if st.button("Reset Project", type="secondary"):
                # TODO: Implement project reset
                st.info("Project reset not yet implemented")
```

**Step 2: Commit**

```bash
git add src/ui/import_panel.py
git commit -m "feat: add CSV import panel

- Drivelog import for new projects
- Nasku import for progress updates
- Error handling with clear messages
- Unmatched UPN validation feedback"
```

---

## Task 14: Streamlit UI - Settings Panel

**Files:**
- Create: `src/ui/settings.py`

**Step 1: Create settings panel**

Create `src/ui/settings.py`:

```python
import streamlit as st

from src.ui.state import get_repository


def render_settings():
    repo = get_repository()
    project = repo.get_project()

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.show_settings = False
        st.rerun()

    st.title("Project Settings")

    if not project:
        st.warning("No project loaded.")
        return

    with st.form("project_settings"):
        st.subheader("General")

        project_name = st.text_input("Project Name", value=project.name)

        st.subheader("Defaults")

        col1, col2 = st.columns(2)

        with col1:
            scan_threshold = st.number_input(
                "Default First Scan Threshold (%)",
                min_value=1,
                max_value=100,
                value=project.default_scan_threshold_pct,
                help="Percentage of piles installed before first scan is triggered",
            )

        with col2:
            pile_rate = st.number_input(
                "Default Pile Rate (piles/day)",
                min_value=1,
                max_value=500,
                value=project.default_pile_rate,
                help="Used for ETA calculation on unstarted inverters",
            )

        st.subheader("Status Color Thresholds")
        st.caption("Days remaining until due date")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.success("Green: 7+ days")
        with col2:
            st.warning("Yellow: 2-6 days")
        with col3:
            st.error("Red: <2 days or overdue")

        st.info("Color thresholds are currently fixed. Future versions may allow customization.")

        st.subheader("Engineer List")
        engineers_default = "Sarah, John, Mike, Lisa"
        engineers = st.text_input(
            "Engineers (comma-separated)",
            value=engineers_default,
            help="Names available in engineer assignment dropdowns",
        )

        submitted = st.form_submit_button("Save Settings")

        if submitted:
            project.name = project_name
            project.default_scan_threshold_pct = scan_threshold
            project.default_pile_rate = pile_rate
            repo.update_project(project)
            st.success("Settings saved!")
            st.rerun()
```

**Step 2: Commit**

```bash
git add src/ui/settings.py
git commit -m "feat: add project settings panel

- Project name editing
- Default scan threshold configuration
- Default pile rate for ETA
- Engineer list management (placeholder)"
```

---

## Task 15: PyInstaller Packaging

**Files:**
- Create: `build.spec`
- Create: `scripts/build.sh`
- Modify: `requirements.txt`

**Step 1: Add PyInstaller to requirements**

Update `requirements.txt` to add:

```txt
streamlit>=1.31.0
supabase>=2.0.0
pandas>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-cov>=4.0.0
pyinstaller>=6.0.0
```

**Step 2: Create PyInstaller spec file**

Create `build.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

import streamlit
import os

streamlit_path = os.path.dirname(streamlit.__file__)

a = Analysis(
    ['src/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        (streamlit_path, 'streamlit'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.runtime.scriptrunner',
        'supabase',
        'pandas',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='InverterTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

**Step 3: Create build script**

Create `scripts/build.sh`:

```bash
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Building executable..."
pyinstaller build.spec --clean

echo "Build complete! Executable at: dist/InverterTracker"
```

**Step 4: Make build script executable and commit**

```bash
chmod +x scripts/build.sh
git add requirements.txt build.spec scripts/build.sh
git commit -m "feat: add PyInstaller packaging for .exe distribution

- PyInstaller spec with Streamlit bundling
- Build script for easy packaging
- Executable output: dist/InverterTracker"
```

---

## Task 16: Integration Testing and Final Polish

**Files:**
- Create: `tests/test_integration.py`
- Create: `.gitignore`

**Step 1: Create integration test**

Create `tests/test_integration.py`:

```python
import pytest
from io import StringIO
from unittest.mock import Mock, patch
from datetime import datetime
from uuid import uuid4

from src.services.import_service import ImportService
from src.services.progress import calculate_progress, calculate_eta
from src.services.alerts import check_milestone_alerts
from src.data.models import Project, Inverter, Pile


DRIVELOG = """Inverter,UPN,Hammering_Status,Hammering_Flag
1,A001,COMPLETED,GOOD
1,A002,COMPLETED,GOOD
1,A003,INCOMPLETE,UNSET
1,A004,INCOMPLETE,UNSET
2,B001,INCOMPLETE,UNSET
2,B002,INCOMPLETE,UNSET
"""

NASKU = """name,processedAt,positioningTime,hammeringTime,hammeringStatus,hammeringFlag
A003,2026-01-20T10:00:00-06:00,50000,80000,COMPLETED,GOOD
A004,2026-01-20T11:00:00-06:00,60000,90000,COMPLETED,GOOD
"""


class TestFullImportFlow:
    def test_drivelog_then_nasku_updates_progress(self):
        # Setup mock repository
        stored_project = None
        stored_inverters = {}
        stored_piles = {}

        repo = Mock()

        def save_project(p):
            nonlocal stored_project
            stored_project = p
            return p

        def save_inverter(i):
            stored_inverters[str(i.id)] = i
            return i

        def save_piles(piles):
            for p in piles:
                key = f"{p.inverter_id}_{p.upn}"
                stored_piles[key] = p
            return piles

        def get_pile_by_upn(inv_id, upn):
            key = f"{inv_id}_{upn}"
            return stored_piles.get(key)

        def update_pile(p):
            key = f"{p.inverter_id}_{p.upn}"
            stored_piles[key] = p
            return p

        repo.get_project.return_value = None
        repo.save_project.side_effect = save_project
        repo.save_inverter.side_effect = save_inverter
        repo.save_piles.side_effect = save_piles
        repo.save_workflow_steps.side_effect = lambda s: s
        repo.get_pile_by_upn.side_effect = get_pile_by_upn
        repo.update_pile.side_effect = update_pile

        # Import drivelog
        service = ImportService(repo)
        project = service.import_drivelog(StringIO(DRIVELOG), "Test Site")

        assert project.name == "Test Site"
        assert len(stored_inverters) == 2

        # Check initial state - inverter 1 has 2 installed, 2 not
        inv1_piles = [p for p in stored_piles.values()
                      if str(p.inverter_id) in [k for k, v in stored_inverters.items() if v.name == "1"]]
        installed_count = sum(1 for p in inv1_piles if p.is_installed)
        assert installed_count == 2

        # Now update repo.get_project to return project
        repo.get_project.return_value = project
        repo.get_inverters.return_value = list(stored_inverters.values())

        def get_piles_for_inverter(inv_id):
            return [p for p in stored_piles.values() if p.inverter_id == inv_id]

        repo.get_piles_for_inverter.side_effect = get_piles_for_inverter

        # Import nasku
        service.import_nasku(StringIO(NASKU))

        # Check updated state - now all 4 piles in inverter 1 should be installed
        inv1_id = next(i.id for i in stored_inverters.values() if i.name == "1")
        inv1_piles = get_piles_for_inverter(inv1_id)
        installed_count = sum(1 for p in inv1_piles if p.is_installed)
        assert installed_count == 4


class TestProgressWithMilestones:
    def test_progress_triggers_milestone_alert(self):
        project = Project(
            id=uuid4(),
            name="Test",
            default_scan_threshold_pct=90,
            default_pile_rate=50,
            created_at=datetime.now(),
        )

        inverter = Inverter(
            id=uuid4(),
            project_id=project.id,
            name="1",
            total_piles=100,
            milestone_thresholds=[25, 50, 75],
            created_at=datetime.now(),
        )

        # Before: 20 piles installed (20%)
        # After: 30 piles installed (30%)
        # Should trigger 25% milestone

        alerts = check_milestone_alerts(
            inverter=inverter,
            previous_percentage=20.0,
            current_percentage=30.0,
        )

        assert len(alerts) == 1
        assert alerts[0].threshold == 25
```

**Step 2: Create .gitignore**

Create `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# PyInstaller
*.manifest
*.spec.bak

# OS
.DS_Store
Thumbs.db

# Project specific
*.csv
*.xls
*.xlsx
```

**Step 3: Run all tests**

Run: `pytest tests/ -v --tb=short`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add tests/test_integration.py .gitignore
git commit -m "feat: add integration tests and gitignore

- Full import flow test (drivelog -> nasku)
- Milestone alert trigger test
- Comprehensive gitignore for Python project"
```

---

## Summary

This plan creates a complete Inverter Tracker Dashboard with:

1. **Tasks 1-6**: Core data models and business logic (models, CSV parsing, import logic, progress/ETA, alerts)
2. **Tasks 7-9**: Data layer (repository interface, Supabase implementation, import orchestration)
3. **Task 10**: Database setup script for Supabase
4. **Tasks 11-14**: Streamlit UI (dashboard grid, expanded card, import panel, settings)
5. **Task 15**: PyInstaller packaging for .exe distribution
6. **Task 16**: Integration testing and project cleanup

Each task follows TDD: write failing test, run to confirm failure, implement, run to confirm pass, commit.

---

**Plan complete and saved to `docs/plans/2026-01-29-implementation-plan.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
