
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.assistant.services import PlanValidationError, validate_project_plan
from apps.planning.models import AcceptanceCriterion, Milestone, Task
from apps.projects.models import Project


class ProjectPlanTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="plan_tester",
            password="test-password-not-for-production",
        )
        self.project = Project.objects.create(
            owner=self.user,
            name="ShipShield Test Project",
            project_type=Project.ProjectType.SOFTWARE,
        )

    def test_valid_plan_can_be_validated_before_saving(self):
        plan = {
            "milestones": [
                {
                    "title": "Build the dashboard",
                    "tasks": [
                        {
                            "title": "Create dashboard layout",
                            "priority": "high",
                            "acceptance_criteria": [
                                "Project summary is visible",
                                "Layout works on mobile",
                            ],
                        }
                    ],
                }
            ]
        }

        validated = validate_project_plan(plan)

        self.assertEqual(
            validated["milestones"][0]["title"],
            "Build the dashboard",
        )

    def test_invalid_plan_is_rejected(self):
        with self.assertRaises(PlanValidationError):
            validate_project_plan({"milestones": []})

    def test_new_project_has_no_milestones_initially(self):
        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            0,
        )
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(AcceptanceCriterion.objects.count(), 0)
        
    
    def test_approved_plan_saves_milestones_tasks_and_criteria(self):
        from apps.planning.services import approve_and_save_plan

        plan = {
            "milestones": [
                {
                    "title": "Build the dashboard",
                    "tasks": [
                        {
                            "title": "Create dashboard layout",
                            "priority": "high",
                            "acceptance_criteria": [
                                "Project summary is visible",
                                "Layout works on mobile",
                            ],
                        }
                    ],
                }
            ]
        }

        milestones = approve_and_save_plan(
            project=self.project,
            user=self.user,
            plan=plan,
        )

        self.assertEqual(len(milestones), 1)
        self.assertEqual(Milestone.objects.filter(project=self.project).count(), 1)
        self.assertEqual(Task.objects.filter(milestone=milestones[0]).count(), 1)
        self.assertEqual(
            AcceptanceCriterion.objects.filter(
                task__milestone=milestones[0]
            ).count(),
            2,
        )

    def test_another_user_cannot_approve_project_plan(self):
        from django.core.exceptions import PermissionDenied
        from apps.planning.services import approve_and_save_plan

        User = get_user_model()
        another_user = User.objects.create_user(
            username="another_tester",
            password="test-password-not-for-production",
        )

        plan = {
            "milestones": [
                {
                    "title": "Unauthorized milestone",
                    "tasks": [
                        {"title": "Unauthorized task"}
                    ],
                }
            ]
        }

        with self.assertRaises(PermissionDenied):
            approve_and_save_plan(
                project=self.project,
                user=another_user,
                plan=plan,
            )

        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            0,
        )