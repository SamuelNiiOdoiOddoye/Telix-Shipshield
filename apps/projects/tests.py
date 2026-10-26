from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.projects.models import Project

User = get_user_model()


class ProjectViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="projectowner",
            password="test-password-123",
        )
        self.other_user = User.objects.create_user(
            username="anotheruser",
            password="test-password-456",
        )
        self.dashboard_url = reverse("projects:dashboard")
        self.create_url = reverse("projects:create")

    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_only_shows_current_users_projects(self):
        own_project = Project.objects.create(
            owner=self.user,
            name="My project",
        )
        Project.objects.create(
            owner=self.other_user,
            name="Someone else's project",
        )

        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, own_project.name)
        self.assertNotContains(response, "Someone else's project")

    def test_create_page_requires_login(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)

    def test_user_can_create_project(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_url,
            {
                "name": "Telix ShipShield",
                "description": "Project execution platform",
                "project_type": "software",
                "goal": "Deliver a working MVP",
                "target_date": "2026-12-31",
            },
        )

        project = Project.objects.get(
            owner=self.user,
            name="Telix ShipShield",
        )

        self.assertRedirects(
            response,
            reverse(
                "projects:detail",
                kwargs={"project_id": project.pk},
            ),
        )
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.project_type, "software")
        self.assertEqual(project.goal, "Deliver a working MVP")

    def test_project_name_is_required(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_url,
            {
                "name": "   ",
                "project_type": "software",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Project name is required.")
        self.assertEqual(Project.objects.count(), 0)

    def test_invalid_project_type_falls_back_to_other(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_url,
            {
                "name": "General project",
                "project_type": "not-a-valid-type",
            },
        )

        project = Project.objects.get(
            owner=self.user,
            name="General project",
        )

        self.assertRedirects(
            response,
            reverse(
                "projects:detail",
                kwargs={"project_id": project.pk},
            ),
        )
        self.assertEqual(
            project.project_type,
            Project.ProjectType.OTHER,
        )



class RegistrationViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="existing_shipshield_user",
            password="Safe-test-password-927!",
        )

    def test_registration_page_is_public(self):
        response = self.client.get(reverse("projects:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create account")

    def test_user_can_register_and_is_logged_in(self):
        response = self.client.post(
            reverse("projects:register"),
            {
                "username": "new_shipshield_user",
                "password1": "Safe-test-password-927!",
                "password2": "Safe-test-password-927!",
            },
        )
        self.assertRedirects(
            response,
            reverse("projects:dashboard"),
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    
    def test_authenticated_user_is_redirected_from_registration(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("projects:register"))
        self.assertRedirects(
            response,
            reverse("projects:dashboard"),
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("projects:register"))
        self.assertRedirects(
            response,
            reverse("projects:dashboard"),
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("projects:register"))
        self.assertRedirects(response, reverse("projects:dashboard"))
