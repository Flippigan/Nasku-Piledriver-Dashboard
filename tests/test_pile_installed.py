# tests/test_pile_installed.py
import pytest

from src.import_.pile_installed import compute_pile_installed


class TestComputePileInstalled:
    def test_refused_flag_returns_refusal(self):
        result = compute_pile_installed("COMPLETED", "REFUSED")
        assert result == "Refusal"

    def test_refused_flag_with_success_returns_refusal(self):
        result = compute_pile_installed("SUCCESS", "REFUSED")
        assert result == "Refusal"

    def test_completed_status_returns_yes(self):
        result = compute_pile_installed("COMPLETED", "GOOD")
        assert result == "Yes"

    def test_success_status_returns_yes(self):
        result = compute_pile_installed("SUCCESS", "NONE")
        assert result == "Yes"

    def test_completed_with_other_flag_returns_yes(self):
        result = compute_pile_installed("COMPLETED", "INCLINED")
        assert result == "Yes"

    def test_incomplete_status_returns_no(self):
        result = compute_pile_installed("INCOMPLETE_NO_FINISH_TIME", "UNSET")
        assert result == "No"

    def test_unattempted_status_returns_no(self):
        result = compute_pile_installed("UNATTEMPTED", "UNSET")
        assert result == "No"

    def test_none_values_return_no(self):
        result = compute_pile_installed(None, None)
        assert result == "No"

    def test_none_status_with_flag_returns_no(self):
        result = compute_pile_installed(None, "GOOD")
        assert result == "No"
