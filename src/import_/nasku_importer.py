from dataclasses import dataclass
from datetime import datetime
from typing import TextIO, BinaryIO
import pandas as pd

from src.import_.csv_parser import parse_csv, validate_required_columns


REQUIRED_COLUMNS = [
    "name", "processedAt", "positioningTime", "hammeringTime",
    "hammeringStatus", "hammeringFlag"
]


class UnmatchedUpnError(Exception):
    def __init__(self, unmatched: set[str]):
        self.unmatched_upns = unmatched
        super().__init__(
            f"Nasku contains UPNs not found in drivelog: {', '.join(sorted(unmatched))}"
        )


@dataclass
class NaskuData:
    updates: dict[str, dict]  # upn -> update dict

    @classmethod
    def from_csv(cls, file: TextIO | BinaryIO) -> "NaskuData":
        df = parse_nasku(file)
        return cls(updates=extract_pile_updates(df))


def parse_nasku(file: TextIO | BinaryIO) -> pd.DataFrame:
    df = parse_csv(file)
    validate_required_columns(df, REQUIRED_COLUMNS)
    return df


def validate_upns_exist(nasku_upns: set[str], existing_upns: set[str]) -> None:
    unmatched = nasku_upns - existing_upns
    if unmatched:
        raise UnmatchedUpnError(unmatched)


def _parse_timestamp(ts_str: str) -> datetime | None:
    if pd.isna(ts_str) or ts_str == "null":
        return None
    # Handle timezone format like "2026-01-16T13:07:21.722-06:00[America/Chicago]"
    # Strip the bracketed timezone name
    if "[" in ts_str:
        ts_str = ts_str.split("[")[0]
    return datetime.fromisoformat(ts_str)


def _parse_time_ms(value) -> float | None:
    if pd.isna(value) or value == "null":
        return None
    # Convert milliseconds to seconds
    return float(value) / 1000.0


def extract_pile_updates(df: pd.DataFrame) -> dict[str, dict]:
    updates = {}
    for _, row in df.iterrows():
        upn = str(row["name"])
        updates[upn] = {
            "hammering_status": row["hammeringStatus"] if pd.notna(row["hammeringStatus"]) else None,
            "hammering_flag": row["hammeringFlag"] if pd.notna(row["hammeringFlag"]) else None,
            "hammering_time_sec": _parse_time_ms(row["hammeringTime"]),
            "positioning_time_sec": _parse_time_ms(row["positioningTime"]),
            "driven_at": _parse_timestamp(row["processedAt"]),
        }
    return updates
