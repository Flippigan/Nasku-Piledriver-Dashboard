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
