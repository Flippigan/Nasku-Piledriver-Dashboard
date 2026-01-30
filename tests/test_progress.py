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
