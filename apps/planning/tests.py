import json
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.assistant.services import PlanValidationError, validate_project_plan
from apps.planning.models import AcceptanceCriterion, Milestone, ProjectPlan ,Task
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

    def test_invalid_plan_creates_no_records(self):
        from apps.planning.services import approve_and_save_plan

        with self.assertRaises(PlanValidationError):
            approve_and_save_plan(
                project=self.project,
                user=self.user,
                plan={"milestones": []},
            )

        self.assertEqual(Milestone.objects.filter(project=self.project).count(), 0)
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(AcceptanceCriterion.objects.count(), 0)

    def test_database_failure_rolls_back_entire_plan(self):
        from unittest.mock import patch

        from apps.planning.services import approve_and_save_plan

        plan = {
            "milestones": [
                {
                    "title": "Build the dashboard",
                    "tasks": [
                        {
                            "title": "Create dashboard layout",
                            "acceptance_criteria": ["Layout renders"],
                        }
                    ],
                }
            ]
        }

        with patch(
            "apps.planning.services.AcceptanceCriterion.objects.create",
            side_effect=RuntimeError("Simulated database failure"),
        ):
            with self.assertRaises(RuntimeError):
                approve_and_save_plan(
                    project=self.project,
                    user=self.user,
                    plan=plan,
                )

        self.assertEqual(Milestone.objects.filter(project=self.project).count(), 0)
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(AcceptanceCriterion.objects.count(), 0)

    def test_project_plan_starts_as_an_editable_draft(self):
        plan_data ={
            "milestones" : [
                {
                    "title": "Build the dashboard",
                    "tasks": [
                        {
                            "title" : "Build the dashboard",
                            "priority" : "high",
                            "acceptance_criteria" : [
                                "The dashboard renders correctly",
                            ],
                        }
                    ],
                }
            ]
        }
        
        draft = ProjectPlan.objects.create(
            project=self.project,
            plan=plan_data,
        )
        
        draft.refresh_from_db()
        
        self.assertEqual(draft.status, ProjectPlan.Status.DRAFT)
        self.assertEqual(draft.plan, plan_data)
        self.assertIsNone(draft.approved_by)
        self.assertIsNone(draft.approved_at)
        
        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            0,
        )


class ProjectPlanWorkflowViewTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="workflow_owner",
            password="test-password-123",
        )
        self.other_user = User.objects.create_user(
            username="workflow_other",
            password="test-password-456",
        )
        self.project = Project.objects.create(
            owner=self.user,
            name="Workflow Test Project",
            project_type=Project.ProjectType.SOFTWARE,
        )

        self.detail_url = reverse(
            "projects:detail",
            kwargs={"project_id": self.project.pk},
        )
        self.edit_url = reverse(
            "planning:plan_edit",
            kwargs={"project_id": self.project.pk},
        )
        self.approve_url = reverse(
            "planning:plan_approve",
            kwargs={"project_id": self.project.pk},
        )

        self.valid_plan = {
            "milestones": [
                {
                    "title": "Build the dashboard",
                    "tasks": [
                        {
                            "title": "Create the dashboard layout",
                            "priority": "high",
                            "acceptance_criteria": [
                                "The project summary is visible",
                                "The layout works on mobile",
                            ],
                        }
                    ],
                }
            ]
        }

    def test_plan_editor_requires_login(self):
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_owner_can_save_draft_without_creating_tasks(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.edit_url,
            {"plan": json.dumps(self.valid_plan)},
        )

        self.assertRedirects(response, self.detail_url)

        draft = ProjectPlan.objects.get(project=self.project)
        self.assertEqual(draft.status, ProjectPlan.Status.DRAFT)
        self.assertEqual(draft.plan, self.valid_plan)

        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            0,
        )
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(AcceptanceCriterion.objects.count(), 0)

    def test_invalid_json_is_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.edit_url,
            {"plan": '{"milestones": '},
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "Enter valid JSON.",
            status_code=400,
        )
        self.assertFalse(
            ProjectPlan.objects.filter(project=self.project).exists()
        )

    def test_another_user_cannot_view_or_change_project_plan(self):
        self.client.force_login(self.other_user)

        detail_response = self.client.get(self.detail_url)
        edit_response = self.client.get(self.edit_url)
        approve_response = self.client.post(self.approve_url)

        self.assertEqual(detail_response.status_code, 403)
        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(approve_response.status_code, 403)

        self.assertFalse(
            ProjectPlan.objects.filter(project=self.project).exists()
        )
        self.assertEqual(Milestone.objects.count(), 0)

    def test_approval_creates_milestones_tasks_and_criteria(self):
        self.client.force_login(self.user)

        self.client.post(
            self.edit_url,
            {"plan": json.dumps(self.valid_plan)},
        )

        response = self.client.post(self.approve_url)

        self.assertRedirects(response, self.detail_url)

        draft = ProjectPlan.objects.get(project=self.project)
        self.assertEqual(draft.status, ProjectPlan.Status.APPROVED)
        self.assertEqual(draft.approved_by, self.user)
        self.assertIsNotNone(draft.approved_at)

        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            1,
        )
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(AcceptanceCriterion.objects.count(), 2)

    def test_duplicate_approval_does_not_duplicate_execution_records(self):
        self.client.force_login(self.user)

        self.client.post(
            self.edit_url,
            {"plan": json.dumps(self.valid_plan)},
        )
        first_response = self.client.post(self.approve_url)

        self.assertRedirects(first_response, self.detail_url)

        second_response = self.client.post(self.approve_url)

        self.assertEqual(second_response.status_code, 400)
        self.assertContains(
            second_response,
            "already been approved",
            status_code=400,
        )

        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            1,
        )
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(AcceptanceCriterion.objects.count(), 2)

    def test_approved_plan_cannot_be_edited_as_a_draft(self):
        self.client.force_login(self.user)

        self.client.post(
            self.edit_url,
            {"plan": json.dumps(self.valid_plan)},
        )
        self.client.post(self.approve_url)

        changed_plan = {
            "milestones": [
                {
                    "title": "A different milestone",
                    "tasks": [
                        {"title": "A different task"}
                    ],
                }
            ]
        }

        response = self.client.post(
            self.edit_url,
            {"plan": json.dumps(changed_plan)},
        )

        self.assertEqual(response.status_code, 400)

        draft = ProjectPlan.objects.get(project=self.project)
        self.assertEqual(draft.status, ProjectPlan.Status.APPROVED)
        self.assertEqual(draft.plan, self.valid_plan)

        self.assertEqual(
            Milestone.objects.filter(project=self.project).count(),
            1,
        )
