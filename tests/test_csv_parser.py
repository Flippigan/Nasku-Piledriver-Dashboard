import pytest
import pandas as pd
from io import StringIO

from src.import_.csv_parser import (
    parse_csv,
    validate_required_columns,
    MissingColumnsError,
)


class TestValidateRequiredColumns:
    def test_passes_when_all_columns_present(self):
        df = pd.DataFrame({"name": ["a"], "status": ["b"], "flag": ["c"]})
        # Should not raise
        validate_required_columns(df, ["name", "status"])

    def test_raises_when_column_missing(self):
        df = pd.DataFrame({"name": ["a"], "status": ["b"]})
        with pytest.raises(MissingColumnsError) as exc:
            validate_required_columns(df, ["name", "status", "flag"])
        assert "flag" in str(exc.value)

    def test_raises_with_multiple_missing_columns(self):
        df = pd.DataFrame({"name": ["a"]})
        with pytest.raises(MissingColumnsError) as exc:
            validate_required_columns(df, ["name", "status", "flag"])
        assert "status" in str(exc.value)
        assert "flag" in str(exc.value)


class TestParseCsv:
    def test_parses_valid_csv(self):
        csv_content = "name,value\na,1\nb,2"
        df = parse_csv(StringIO(csv_content))
        assert len(df) == 2
        assert list(df.columns) == ["name", "value"]

    def test_raises_on_empty_file(self):
        with pytest.raises(ValueError, match="empty"):
            parse_csv(StringIO(""))

    def test_handles_whitespace_in_headers(self):
        csv_content = " name , value \na,1"
        df = parse_csv(StringIO(csv_content))
        assert list(df.columns) == ["name", "value"]
