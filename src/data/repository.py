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
