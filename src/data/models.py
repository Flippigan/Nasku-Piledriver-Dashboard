from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, computed_field


class Project(BaseModel):
    id: UUID
    name: str
    default_scan_threshold_pct: int
    default_pile_rate: int
    created_at: datetime


class Inverter(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    total_piles: int
    scan_threshold_override: Optional[int] = None
    milestone_thresholds: list[int] = [50, 75, 90]
    created_at: datetime


class Pile(BaseModel):
    id: UUID
    inverter_id: UUID
    upn: str
    pile_installed: str = "No"  # "Yes", "No", or "Refusal"
    hammering_status: Optional[str] = None
    hammering_flag: Optional[str] = None
    hammering_time_sec: Optional[float] = None
    positioning_time_sec: Optional[float] = None
    driven_at: Optional[datetime] = None

    @computed_field
    @property
    def is_installed(self) -> bool:
        return self.pile_installed == "Yes"


class WorkflowStep(BaseModel):
    id: UUID
    inverter_id: UUID
    step_name: str
    step_order: int
    is_complete: bool = False
    completed_at: Optional[datetime] = None
    due_date: Optional[date] = None
    assigned_engineer: Optional[str] = None


class Alert(BaseModel):
    id: UUID
    inverter_id: UUID
    alert_type: str
    threshold_value: int
    acknowledged: bool = False
    created_at: datetime
