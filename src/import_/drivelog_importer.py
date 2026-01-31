from dataclasses import dataclass
from typing import TextIO, BinaryIO
import pandas as pd

from src.import_.csv_parser import parse_csv, validate_required_columns


REQUIRED_COLUMNS = ["Inverter", "UPN", "Hammering_Status", "Hammering_Flag"]
OPTIONAL_COLUMNS = ["Pile_Installed"]


@dataclass
class PileData:
    upn: str
    hammering_status: str | None
    hammering_flag: str | None


@dataclass
class DrivelogData:
    inverters: dict[str, int]  # inverter_name -> pile_count
    piles: dict[str, list[dict]]  # inverter_name -> list of pile dicts

    @classmethod
    def from_csv(cls, file: TextIO | BinaryIO) -> "DrivelogData":
        df = parse_drivelog(file)
        return cls(
            inverters=extract_inverters(df),
            piles=extract_piles(df),
        )


def parse_drivelog(file: TextIO | BinaryIO) -> pd.DataFrame:
    df = parse_csv(file)
    validate_required_columns(df, REQUIRED_COLUMNS)

    # Keep required columns plus optional if present
    columns_to_keep = REQUIRED_COLUMNS.copy()
    for col in OPTIONAL_COLUMNS:
        if col in df.columns:
            columns_to_keep.append(col)

    df = df[columns_to_keep].copy()

    # Handle duplicate UPNs - keep first occurrence
    df = df.drop_duplicates(subset=["UPN"], keep="first")

    return df


def extract_inverters(df: pd.DataFrame) -> dict[str, int]:
    # Convert Inverter to string for consistent keys
    df["Inverter"] = df["Inverter"].astype(str)
    return df.groupby("Inverter").size().to_dict()


def extract_piles(df: pd.DataFrame) -> dict[str, list[dict]]:
    df["Inverter"] = df["Inverter"].astype(str)
    has_pile_installed = "Pile_Installed" in df.columns

    result: dict[str, list[dict]] = {}
    for inverter_name, group in df.groupby("Inverter"):
        result[str(inverter_name)] = [
            {
                "upn": str(row["UPN"]),
                "hammering_status": row["Hammering_Status"] if pd.notna(row["Hammering_Status"]) else None,
                "hammering_flag": row["Hammering_Flag"] if pd.notna(row["Hammering_Flag"]) else None,
                "pile_installed": row["Pile_Installed"] if has_pile_installed and pd.notna(row["Pile_Installed"]) else "No",
            }
            for _, row in group.iterrows()
        ]
    return result
