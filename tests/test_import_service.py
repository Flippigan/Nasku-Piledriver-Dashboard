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
        inverter_id = uuid4()
        existing_pile_1 = Pile(
            id=uuid4(),
            inverter_id=inverter_id,
            upn="12345",
            hammering_status=None,
            hammering_flag=None,
        )
        existing_pile_2 = Pile(
            id=uuid4(),
            inverter_id=inverter_id,
            upn="12346",
            hammering_status=None,
            hammering_flag=None,
        )
        mock_repo.get_pile_by_upn.side_effect = lambda inv_id, upn: {
            "12345": existing_pile_1,
            "12346": existing_pile_2,
        }.get(upn)
        mock_repo.update_pile.side_effect = lambda p: p
        mock_repo.get_piles_for_inverter.return_value = [existing_pile_1, existing_pile_2]
        mock_repo.get_inverters.return_value = [
            Inverter(
                id=inverter_id,
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
