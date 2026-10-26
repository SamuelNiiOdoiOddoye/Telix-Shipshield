
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError, transaction
from django.test import TestCase, SimpleTestCase

from apps.projects.models import Project
from apps.planning.models import (
    AcceptanceCriterion,
    Milestone,
    Task,
)

from apps.assistant.services import(
    PlanValidationError,
    validate_project_plan
)

from apps.planning.services import approve_and_save_plan


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


class ApproveAndSavePlanTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="shipshield-test-user",
            password="test-password-123",
        )
        self.project = Project.objects.create(
            owner=self.user,
            name="Dashboard Project",
            project_type=Project.ProjectType.SOFTWARE,
        )

    def valid_plan(self):
        return {
            "milestones": [
                {
                    "title": "Build the dashboard",
                    "description": "Create the first dashboard release.",
                    "tasks": [
                        {
                            "title": "Create dashboard layout",
                            "description": "Implement the responsive layout.",
                            "priority": "high",
                            "acceptance_criteria": [
                                "Dashboard displays project summary",
                                "Layout works on mobile screens",
                            ],
                        },
                        {
                            "title": "Add navigation",
                            "priority": "medium",
                            "acceptance_criteria": [
                                "Users can navigate between pages",
                            ],
                        },
                    ],
                },
                {
                    "title": "Test the dashboard",
                    "tasks": [
                        {
                            "title": "Run dashboard tests",
                            "priority": "critical",
                            "acceptance_criteria": [
                                "All dashboard tests pass",
                            ],
                        }
                    ],
                },
            ]
        }

    def test_saves_milestones_tasks_and_acceptance_criteria(self):
        created_milestones = approve_and_save_plan(
            project=self.project,
            user=self.user,
            plan=self.valid_plan(),
        )

        self.assertEqual(len(created_milestones), 2)
        self.assertEqual(
            sum(
                milestone.tasks.count()
                for milestone in created_milestones
            ),
            3,
        )

        milestones = Milestone.objects.filter(
            project=self.project
        )
        self.assertEqual(milestones.count(), 2)

        tasks = Task.objects.filter(
            milestone__project=self.project
        )
        self.assertEqual(tasks.count(), 3)

        criteria = AcceptanceCriterion.objects.filter(
            task__milestone__project=self.project
        )
        self.assertEqual(criteria.count(), 4)

        first_milestone = milestones.get(
            title="Build the dashboard"
        )
        self.assertEqual(first_milestone.order, 0)
        self.assertEqual(
            first_milestone.description,
            "Create the first dashboard release.",
        )

        layout_task = tasks.get(
            title="Create dashboard layout"
        )
        self.assertEqual(layout_task.priority, Task.Priority.HIGH)
        self.assertEqual(
            layout_task.acceptance_criteria.count(),
            2,
        )

    def test_saved_records_belong_to_the_correct_project(self):
        other_project = Project.objects.create(
            owner=self.user,
            name="Another Project",
            project_type=Project.ProjectType.OTHER,
        )

        approve_and_save_plan(
            project=self.project,
            user=self.user,
            plan=self.valid_plan(),
        )

        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            2,
        )
        self.assertEqual(
            Milestone.objects.filter(project=other_project).count(),
            0,
        )

    def test_invalid_plan_creates_no_records(self):
        invalid_plan = {
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
            approve_and_save_plan(
                project=self.project,
                user=self.user,
                plan=invalid_plan,
            )

        self.assertEqual(Milestone.objects.count(), 0)
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(AcceptanceCriterion.objects.count(), 0)

    def test_database_error_rolls_back_all_records(self):
        original_create = Task.objects.create

        def fail_task_creation(*args, **kwargs):
            raise DatabaseError("Simulated task creation failure")

        with patch.object(
            Task.objects,
            "create",
            side_effect=fail_task_creation,
        ):
            with self.assertRaises(DatabaseError):
                # Catch the database error outside the atomic block.
                with transaction.atomic():
                    approve_and_save_plan(
                        project=self.project,
                        user=self.user,
                        plan=self.valid_plan(),
                    )

        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            0,
        )
        self.assertEqual(
            Task.objects.filter(
                milestone__project=self.project
            ).count(),
            0,
        )
        self.assertEqual(
            AcceptanceCriterion.objects.filter(
                task__milestone__project=self.project
            ).count(),
            0,
        )
