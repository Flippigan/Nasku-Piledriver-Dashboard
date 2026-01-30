from dataclasses import dataclass

from src.data.models import Inverter, Alert


@dataclass
class AlertCheck:
    inverter_id: str
    threshold: int
    alert_type: str = "milestone_reached"


def check_milestone_alerts(
    inverter: Inverter,
    previous_percentage: float,
    current_percentage: float,
) -> list[AlertCheck]:
    crossed = []

    for threshold in inverter.milestone_thresholds:
        # Milestone is crossed if we went from below to at-or-above
        if previous_percentage < threshold <= current_percentage:
            crossed.append(AlertCheck(
                inverter_id=str(inverter.id),
                threshold=threshold,
            ))

    return crossed


def get_pending_alerts(alerts: list[Alert]) -> list[Alert]:
    return [a for a in alerts if not a.acknowledged]
