from typing import BinaryIO, TextIO
import pandas as pd


class MissingColumnsError(Exception):
    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(f"Missing required columns: {', '.join(missing)}")


def validate_required_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise MissingColumnsError(missing)


def parse_csv(file: TextIO | BinaryIO) -> pd.DataFrame:
    try:
        df = pd.read_csv(file)
    except pd.errors.EmptyDataError:
        raise ValueError("File is empty")

    if df.empty and len(df.columns) == 0:
        raise ValueError("File is empty")

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    return df
