import pytest
from uuid import uuid4

from src.data.workflow import WORKFLOW_STEPS, create_workflow_steps


class TestWorkflowSteps:
    def test_has_eleven_steps(self):
        assert len(WORKFLOW_STEPS) == 11

    def test_steps_are_ordered(self):
        for i, step in enumerate(WORKFLOW_STEPS, start=1):
            assert step["order"] == i

    def test_first_step_is_first_scan(self):
        assert WORKFLOW_STEPS[0]["name"] == "First Scan"

    def test_last_step_is_walk_down(self):
        assert WORKFLOW_STEPS[-1]["name"] == "Walk Down"


class TestCreateWorkflowSteps:
    def test_creates_eleven_steps_for_inverter(self):
        inverter_id = uuid4()
        steps = create_workflow_steps(inverter_id)

        assert len(steps) == 11
        for step in steps:
            assert step.inverter_id == inverter_id
            assert step.is_complete is False

    def test_steps_have_correct_order(self):
        steps = create_workflow_steps(uuid4())
        orders = [s.step_order for s in steps]
        assert orders == list(range(1, 12))

    def test_each_step_has_unique_id(self):
        steps = create_workflow_steps(uuid4())
        ids = [s.id for s in steps]
        assert len(ids) == len(set(ids))
