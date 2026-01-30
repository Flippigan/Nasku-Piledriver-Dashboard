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
