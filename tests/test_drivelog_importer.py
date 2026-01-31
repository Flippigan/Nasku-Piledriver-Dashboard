import pytest
import pandas as pd
from io import StringIO
from uuid import uuid4

from src.import_.drivelog_importer import (
    parse_drivelog,
    extract_inverters,
    extract_piles,
    DrivelogData,
)
from src.import_.csv_parser import MissingColumnsError


SAMPLE_DRIVELOG = """OBJECTID,Inverter,Row,Table_,UPN,Hammering_Status,Hammering_Flag,Other_Column
1,1,40,360,41659,COMPLETED,GOOD,ignored
2,1,41,361,41660,COMPLETED,GOOD,ignored
3,2,10,100,50001,INCOMPLETE,UNSET,ignored
4,2,11,101,50002,COMPLETED,BAD,ignored
"""


class TestParseDrivelog:
    def test_extracts_required_columns_only(self):
        result = parse_drivelog(StringIO(SAMPLE_DRIVELOG))
        assert set(result.columns) == {"Inverter", "UPN", "Hammering_Status", "Hammering_Flag"}

    def test_raises_on_missing_required_column(self):
        bad_csv = "OBJECTID,Row,UPN\n1,40,41659"
        with pytest.raises(MissingColumnsError) as exc:
            parse_drivelog(StringIO(bad_csv))
        assert "Inverter" in str(exc.value)

    def test_handles_duplicate_upns_keeps_first(self):
        csv_with_dupe = """Inverter,UPN,Hammering_Status,Hammering_Flag
1,12345,COMPLETED,GOOD
1,12345,INCOMPLETE,UNSET
"""
        result = parse_drivelog(StringIO(csv_with_dupe))
        assert len(result) == 1
        assert result.iloc[0]["Hammering_Status"] == "COMPLETED"


class TestExtractInverters:
    def test_extracts_unique_inverters_with_pile_counts(self):
        df = parse_drivelog(StringIO(SAMPLE_DRIVELOG))
        inverters = extract_inverters(df)

        assert len(inverters) == 2
        assert inverters["1"] == 2  # Inverter 1 has 2 piles
        assert inverters["2"] == 2  # Inverter 2 has 2 piles


class TestExtractPiles:
    def test_extracts_piles_grouped_by_inverter(self):
        df = parse_drivelog(StringIO(SAMPLE_DRIVELOG))
        piles = extract_piles(df)

        assert "1" in piles
        assert "2" in piles
        assert len(piles["1"]) == 2
        assert piles["1"][0]["upn"] == "41659"
        assert piles["1"][0]["hammering_status"] == "COMPLETED"
        assert piles["1"][0]["hammering_flag"] == "GOOD"


class TestDrivelogData:
    def test_full_parse_returns_structured_data(self):
        data = DrivelogData.from_csv(StringIO(SAMPLE_DRIVELOG))

        assert len(data.inverters) == 2
        assert data.inverters["1"] == 2
        assert len(data.piles["1"]) == 2
        assert len(data.piles["2"]) == 2


DRIVELOG_WITH_PILE_INSTALLED = """Inverter,UPN,Hammering_Status,Hammering_Flag,Pile_Installed
1,41659,COMPLETED,GOOD,Yes
1,41660,COMPLETED,REFUSED,Refusal
2,50001,INCOMPLETE,UNSET,No
"""


class TestExtractPilesWithPileInstalled:
    def test_extracts_pile_installed_when_present(self):
        df = parse_drivelog(StringIO(DRIVELOG_WITH_PILE_INSTALLED))
        piles = extract_piles(df)

        assert piles["1"][0]["pile_installed"] == "Yes"
        assert piles["1"][1]["pile_installed"] == "Refusal"
        assert piles["2"][0]["pile_installed"] == "No"

    def test_defaults_pile_installed_to_no_when_missing(self):
        df = parse_drivelog(StringIO(SAMPLE_DRIVELOG))
        piles = extract_piles(df)

        # When Pile_Installed column is missing, should default to "No"
        assert piles["1"][0]["pile_installed"] == "No"
