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
