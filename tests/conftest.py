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
