from uuid import uuid4, UUID

from src.data.models import WorkflowStep


WORKFLOW_STEPS = [
    {"order": 1, "name": "First Scan"},
    {"order": 2, "name": "Processed"},
    {"order": 3, "name": "Points Picked"},
    {"order": 4, "name": "Pushed to ArcGIS"},
    {"order": 5, "name": "Remediation Performed"},
    {"order": 6, "name": "Second Scan Complete"},
    {"order": 7, "name": "Processed"},
    {"order": 8, "name": "Points Picked"},
    {"order": 9, "name": "Pushed to ArcGIS"},
    {"order": 10, "name": "Second Remediation Performed"},
    {"order": 11, "name": "Walk Down"},
]


def create_workflow_steps(inverter_id: UUID) -> list[WorkflowStep]:
    return [
        WorkflowStep(
            id=uuid4(),
            inverter_id=inverter_id,
            step_name=step["name"],
            step_order=step["order"],
            is_complete=False,
            completed_at=None,
            due_date=None,
            assigned_engineer=None,
        )
        for step in WORKFLOW_STEPS
    ]
