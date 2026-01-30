from dataclasses import dataclass
from datetime import datetime, timedelta

from src.data.models import Inverter, Pile


@dataclass
class ProgressStats:
    installed_count: int
    total_count: int
    percentage: float


@dataclass
class EtaStats:
    remaining_piles: int
    piles_per_day: float
    is_using_default_rate: bool
    estimated_completion: datetime | None


def calculate_progress(inverter: Inverter, piles: list[Pile]) -> ProgressStats:
    installed = sum(1 for p in piles if p.is_installed)
    total = inverter.total_piles

    if total == 0:
        percentage = 0.0
    else:
        percentage = (installed / total) * 100

    return ProgressStats(
        installed_count=installed,
        total_count=total,
        percentage=percentage,
    )


def calculate_pile_rate(piles: list[Pile]) -> float | None:
    installed_piles = [p for p in piles if p.is_installed and p.driven_at]

    if not installed_piles:
        return None

    # Find earliest driven_at
    earliest = min(p.driven_at for p in installed_piles)
    now = datetime.now()

    # Calculate days elapsed
    elapsed = now - earliest
    days = elapsed.total_seconds() / (24 * 60 * 60)

    if days < 0.001:  # Avoid division by very small numbers
        return None

    return len(installed_piles) / days


def calculate_eta(
    inverter: Inverter,
    piles: list[Pile],
    default_rate: int,
) -> EtaStats:
    progress = calculate_progress(inverter, piles)
    remaining = inverter.total_piles - progress.installed_count

    if remaining <= 0:
        return EtaStats(
            remaining_piles=0,
            piles_per_day=0.0,
            is_using_default_rate=False,
            estimated_completion=None,
        )

    actual_rate = calculate_pile_rate(piles)

    if actual_rate is not None:
        rate = actual_rate
        using_default = False
    else:
        rate = float(default_rate)
        using_default = True

    if rate > 0:
        days_remaining = remaining / rate
        completion = datetime.now() + timedelta(days=days_remaining)
    else:
        completion = None

    return EtaStats(
        remaining_piles=remaining,
        piles_per_day=rate,
        is_using_default_rate=using_default,
        estimated_completion=completion,
    )
