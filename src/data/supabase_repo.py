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
        # Exclude computed field 'is_installed' - it's derived from pile_installed
        data = [p.model_dump(mode="json", exclude={"is_installed"}) for p in piles]
        result = self.client.table("piles").insert(data).execute()
        return [Pile(**row) for row in result.data]

    def update_pile(self, pile: Pile) -> Pile:
        # Exclude computed field 'is_installed' - it's derived from pile_installed
        data = pile.model_dump(mode="json", exclude={"is_installed"})
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

    # Reset methods
    def reset_all(self) -> None:
        """Delete all data. Order matters: children before parents (FK constraints)."""
        # Supabase requires a filter - use neq with impossible UUID to match all
        _ALL = "00000000-0000-0000-0000-000000000000"
        self.client.table("alerts").delete().neq("id", _ALL).execute()
        self.client.table("workflow_steps").delete().neq("id", _ALL).execute()
        self.client.table("piles").delete().neq("id", _ALL).execute()
        self.client.table("inverters").delete().neq("id", _ALL).execute()
        self.client.table("projects").delete().neq("id", _ALL).execute()
