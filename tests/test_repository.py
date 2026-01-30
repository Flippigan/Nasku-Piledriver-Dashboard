import pytest
from abc import ABC
from uuid import uuid4
from datetime import datetime

from src.data.repository import Repository
from src.data.models import Project, Inverter, Pile, WorkflowStep, Alert


class TestRepositoryInterface:
    def test_repository_is_abstract(self):
        assert issubclass(Repository, ABC)

    def test_repository_has_project_methods(self):
        assert hasattr(Repository, "get_project")
        assert hasattr(Repository, "save_project")
        assert hasattr(Repository, "update_project")

    def test_repository_has_inverter_methods(self):
        assert hasattr(Repository, "get_inverters")
        assert hasattr(Repository, "get_inverter")
        assert hasattr(Repository, "save_inverter")
        assert hasattr(Repository, "update_inverter")

    def test_repository_has_pile_methods(self):
        assert hasattr(Repository, "get_piles_for_inverter")
        assert hasattr(Repository, "save_piles")
        assert hasattr(Repository, "update_pile")

    def test_repository_has_workflow_methods(self):
        assert hasattr(Repository, "get_workflow_steps")
        assert hasattr(Repository, "save_workflow_steps")
        assert hasattr(Repository, "update_workflow_step")

    def test_repository_has_alert_methods(self):
        assert hasattr(Repository, "get_alerts_for_inverter")
        assert hasattr(Repository, "save_alert")
        assert hasattr(Repository, "acknowledge_alert")
