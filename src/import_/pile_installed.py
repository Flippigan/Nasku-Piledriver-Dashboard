# src/import_/pile_installed.py
def compute_pile_installed(
    hammering_status: str | None,
    hammering_flag: str | None,
) -> str:
    """
    Compute Pile_Installed from hammering columns.
    Used during Nasku CSV import (which has no Pile_Installed column).

    Returns: "Yes", "No", or "Refusal"
    """
    if hammering_flag == "REFUSED":
        return "Refusal"

    if hammering_status in ("COMPLETED", "SUCCESS"):
        return "Yes"

    return "No"
