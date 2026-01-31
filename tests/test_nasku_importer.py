import pytest
import pandas as pd
from io import StringIO
from datetime import datetime

from src.import_.nasku_importer import (
    parse_nasku,
    validate_upns_exist,
    extract_pile_updates,
    NaskuData,
    UnmatchedUpnError,
)
from src.import_.csv_parser import MissingColumnsError


SAMPLE_NASKU = """name,processedAt,machine,positioningTime,hammeringTime,hammeringStatus,hammeringFlag,resultEasting,resultNorthing,resultAltitude
27117,2026-01-16T13:07:21.722-06:00[America/Chicago],Machine_4,null,17870,COMPLETED,GOOD,689158.07,111718.79,276.68
29852,2026-01-16T13:37:11.499-06:00[America/Chicago],Machine_4,80500,165181,COMPLETED,GOOD,689181.83,111710.68,276.21
47574,2026-01-03T07:27:51.821-06:00[America/Chicago],Machine_3,null,147725,INCOMPLETE_NO_FINISH_TIME,UNSET,null,null,null
"""


class TestParseNasku:
    def test_extracts_required_columns(self):
        result = parse_nasku(StringIO(SAMPLE_NASKU))
        expected_cols = {"name", "processedAt", "positioningTime", "hammeringTime",
                        "hammeringStatus", "hammeringFlag"}
        assert expected_cols.issubset(set(result.columns))

    def test_raises_on_missing_column(self):
        bad_csv = "name,processedAt\n12345,2026-01-16"
        with pytest.raises(MissingColumnsError) as exc:
            parse_nasku(StringIO(bad_csv))
        assert "hammeringStatus" in str(exc.value)


class TestValidateUpnsExist:
    def test_passes_when_all_upns_exist(self):
        nasku_upns = {"27117", "29852"}
        existing_upns = {"27117", "29852", "99999"}
        # Should not raise
        validate_upns_exist(nasku_upns, existing_upns)

    def test_raises_when_upn_not_found(self):
        nasku_upns = {"27117", "29852", "UNKNOWN"}
        existing_upns = {"27117", "29852"}
        with pytest.raises(UnmatchedUpnError) as exc:
            validate_upns_exist(nasku_upns, existing_upns)
        assert "UNKNOWN" in exc.value.unmatched_upns


class TestExtractPileUpdates:
    def test_extracts_update_data(self):
        df = parse_nasku(StringIO(SAMPLE_NASKU))
        updates = extract_pile_updates(df)

        assert len(updates) == 3
        assert updates["27117"]["hammering_status"] == "COMPLETED"
        assert updates["27117"]["hammering_flag"] == "GOOD"
        assert updates["27117"]["hammering_time_sec"] == 17.870  # Converted from ms
        assert updates["27117"]["positioning_time_sec"] is None  # Was "null"

    def test_parses_timestamp(self):
        df = parse_nasku(StringIO(SAMPLE_NASKU))
        updates = extract_pile_updates(df)

        assert updates["27117"]["driven_at"] is not None
        assert isinstance(updates["27117"]["driven_at"], datetime)


class TestNaskuData:
    def test_from_csv_returns_structured_data(self):
        data = NaskuData.from_csv(StringIO(SAMPLE_NASKU))

        assert len(data.updates) == 3
        assert "27117" in data.updates
        assert data.updates["29852"]["positioning_time_sec"] == 80.5  # ms -> sec


class TestExtractPileUpdatesWithPileInstalled:
    def test_computes_pile_installed_yes_for_completed(self):
        df = parse_nasku(StringIO(SAMPLE_NASKU))
        updates = extract_pile_updates(df)

        # COMPLETED + GOOD = Yes
        assert updates["27117"]["pile_installed"] == "Yes"
        # COMPLETED + GOOD = Yes
        assert updates["29852"]["pile_installed"] == "Yes"

    def test_computes_pile_installed_no_for_incomplete(self):
        df = parse_nasku(StringIO(SAMPLE_NASKU))
        updates = extract_pile_updates(df)

        # INCOMPLETE_NO_FINISH_TIME + UNSET = No
        assert updates["47574"]["pile_installed"] == "No"


NASKU_WITH_REFUSAL = """name,processedAt,positioningTime,hammeringTime,hammeringStatus,hammeringFlag
12345,2026-01-16T13:07:21.722-06:00,80000,17870,COMPLETED,REFUSED
"""


class TestExtractPileUpdatesRefusal:
    def test_computes_pile_installed_refusal_for_refused_flag(self):
        df = parse_nasku(StringIO(NASKU_WITH_REFUSAL))
        updates = extract_pile_updates(df)

        assert updates["12345"]["pile_installed"] == "Refusal"
