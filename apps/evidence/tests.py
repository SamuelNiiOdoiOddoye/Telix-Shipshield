from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.evidence.models import Evidence
from apps.planning.models import Milestone, Task
from apps.projects.models import Project


class EvidenceViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="evidence_owner", password="test-password-123")
        self.other = User.objects.create_user(username="evidence_other", password="test-password-456")
        self.project = Project.objects.create(owner=self.owner, name="Evidence test project")
        milestone = Milestone.objects.create(project=self.project, title="Delivery")
        self.task = Task.objects.create(milestone=milestone, title="Verify output")
        self.url = reverse("evidence:add", kwargs={"project_id": self.project.pk, "task_id": self.task.pk})

    def test_owner_can_add_evidence_to_project_task(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, {
            "title": "Review notes",
            "description": "The result was checked against the acceptance criteria.",
            "url": "https://example.com/evidence",
            "evidence_type": "link",
        })
        self.assertRedirects(response, reverse("projects:detail", kwargs={"project_id": self.project.pk}))
        evidence = Evidence.objects.get(task=self.task)
        self.assertEqual(evidence.submitted_by, self.owner)
        self.assertEqual(evidence.title, "Review notes")

    def test_other_user_cannot_add_evidence_to_project(self):
        self.client.force_login(self.other)
        response = self.client.post(self.url, {"title": "Not allowed", "evidence_type": "note"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Evidence.objects.exists())
