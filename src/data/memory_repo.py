"""In-memory repository for testing without Supabase."""

from datetime import datetime
from uuid import UUID, uuid4

from src.data.repository import Repository
from src.data.models import Project, Inverter, Pile, WorkflowStep, Alert
from src.data.workflow import create_workflow_steps


class MemoryRepository(Repository):
    """In-memory implementation for local testing without database."""

    def __init__(self):
        self._project: Project | None = None
        self._inverters: dict[UUID, Inverter] = {}
        self._piles: dict[UUID, Pile] = {}
        self._workflow_steps: dict[UUID, WorkflowStep] = {}
        self._alerts: dict[UUID, Alert] = {}

        # Load demo data
        self._load_demo_data()

    def _load_demo_data(self):
        """Create sample data for testing."""
        # Create project
        self._project = Project(
            id=uuid4(),
            name="Demo Solar Site",
            default_scan_threshold_pct=90,
            default_pile_rate=50,
            created_at=datetime.now(),
        )

        # Create 6 inverters with varying progress
        inverter_configs = [
            ("INV-01", 2000, 1800),  # 90% complete
            ("INV-02", 2000, 1500),  # 75% complete
            ("INV-03", 2000, 1000),  # 50% complete
            ("INV-04", 2000, 500),   # 25% complete
            ("INV-05", 2000, 100),   # 5% complete
            ("INV-06", 2000, 0),     # 0% complete
        ]

        for name, total, installed_count in inverter_configs:
            inv = Inverter(
                id=uuid4(),
                project_id=self._project.id,
                name=name,
                total_piles=total,
                milestone_thresholds=[25, 50, 75, 90],
                created_at=datetime.now(),
            )
            self._inverters[inv.id] = inv

            # Create piles
            for i in range(total):
                is_installed = i < installed_count
                pile = Pile(
                    id=uuid4(),
                    inverter_id=inv.id,
                    upn=f"{name}-{i+1:04d}",
                    hammering_status="COMPLETED" if is_installed else "INCOMPLETE",
                    hammering_flag="GOOD" if is_installed else "UNSET",
                    hammering_time_sec=150.0 if is_installed else None,
                    positioning_time_sec=80.0 if is_installed else None,
                    driven_at=datetime.now() if is_installed else None,
                )
                self._piles[pile.id] = pile

            # Create workflow steps
            steps = create_workflow_steps(inv.id)
            for step in steps:
                self._workflow_steps[step.id] = step

    # Project methods
    def get_project(self) -> Project | None:
        return self._project

    def save_project(self, project: Project) -> Project:
        self._project = project
        return project

    def update_project(self, project: Project) -> Project:
        self._project = project
        return project

    # Inverter methods
    def get_inverters(self, project_id: UUID) -> list[Inverter]:
        return [
            inv for inv in self._inverters.values()
            if inv.project_id == project_id
        ]

    def get_inverter(self, inverter_id: UUID) -> Inverter | None:
        return self._inverters.get(inverter_id)

    def save_inverter(self, inverter: Inverter) -> Inverter:
        self._inverters[inverter.id] = inverter
        return inverter

    def update_inverter(self, inverter: Inverter) -> Inverter:
        self._inverters[inverter.id] = inverter
        return inverter

    # Pile methods
    def get_piles_for_inverter(self, inverter_id: UUID) -> list[Pile]:
        return [
            pile for pile in self._piles.values()
            if pile.inverter_id == inverter_id
        ]

    def save_piles(self, piles: list[Pile]) -> list[Pile]:
        for pile in piles:
            self._piles[pile.id] = pile
        return piles

    def update_pile(self, pile: Pile) -> Pile:
        self._piles[pile.id] = pile
        return pile

    def get_pile_by_upn(self, inverter_id: UUID, upn: str) -> Pile | None:
        for pile in self._piles.values():
            if pile.inverter_id == inverter_id and pile.upn == upn:
                return pile
        return None

    # Workflow methods
    def get_workflow_steps(self, inverter_id: UUID) -> list[WorkflowStep]:
        steps = [
            step for step in self._workflow_steps.values()
            if step.inverter_id == inverter_id
        ]
        return sorted(steps, key=lambda s: s.step_order)

    def save_workflow_steps(self, steps: list[WorkflowStep]) -> list[WorkflowStep]:
        for step in steps:
            self._workflow_steps[step.id] = step
        return steps

    def update_workflow_step(self, step: WorkflowStep) -> WorkflowStep:
        self._workflow_steps[step.id] = step
        return step

    # Alert methods
    def get_alerts_for_inverter(self, inverter_id: UUID) -> list[Alert]:
        alerts = [
            alert for alert in self._alerts.values()
            if alert.inverter_id == inverter_id
        ]
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)

    def save_alert(self, alert: Alert) -> Alert:
        self._alerts[alert.id] = alert
        return alert

    def acknowledge_alert(self, alert_id: UUID) -> Alert:
        alert = self._alerts[alert_id]
        alert.acknowledged = True
        return alert

    # Reset methods
    def reset_all(self) -> None:
        self._project = None
        self._inverters.clear()
        self._piles.clear()
        self._workflow_steps.clear()
        self._alerts.clear()
