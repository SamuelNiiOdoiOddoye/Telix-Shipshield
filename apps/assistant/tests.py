
from django.test import SimpleTestCase

from .services import PlanValidationError, validate_project_plan


class ValidateProjectPlanTests(SimpleTestCase):
    def test_accepts_valid_plan(self):
        plan = {
            "milestones": [
                {
                    "title": "Build the dashboard",
                    "tasks": [
                        {
                            "title": "Create dashboard layout",
                            "priority": "high",
                            "acceptance_criteria": [
                                "Dashboard displays project summary",
                                "Layout works on mobile screens",
                            ],
                        }
                    ],
                }
            ]
        }

        self.assertEqual(validate_project_plan(plan), plan)

    def test_rejects_plan_without_milestones(self):
        with self.assertRaises(PlanValidationError):
            validate_project_plan({"milestones": []})

    def test_rejects_milestone_without_title(self):
        plan = {
            "milestones": [
                {
                    "title": " ",
                    "tasks": [{"title": "Create layout"}],
                }
            ]
        }

        with self.assertRaises(PlanValidationError):
            validate_project_plan(plan)

    def test_rejects_task_with_invalid_priority(self):
        plan = {
            "milestones": [
                {
                    "title": "Build dashboard",
                    "tasks": [
                        {
                            "title": "Create layout",
                            "priority": "urgent",
                        }
                    ],
                }
            ]
        }

        with self.assertRaises(PlanValidationError):
            validate_project_plan(plan)
