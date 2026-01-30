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
