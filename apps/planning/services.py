
from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.assistant.services import validate_project_plan
from apps.planning.models import AcceptanceCriterion, Milestone, Task
from apps.projects.models import Project


@transaction.atomic
def approve_and_save_plan(*, project: Project, user, plan: dict) -> list[Milestone]:
    """
    Validate and save an approved project plan.

    Call this function only after the user explicitly approves the plan.
    Returns the milestones created for the project.
    """
    if project.owner != user:
        raise PermissionDenied(
            "You do not have permission to approve this project's plan."
        )

    validated_plan = validate_project_plan(plan)
    created_milestones = []

    for milestone_index, milestone_data in enumerate(
        validated_plan["milestones"]
    ):
        milestone = Milestone.objects.create(
            project=project,
            title=milestone_data["title"].strip(),
            description=milestone_data.get("description", "").strip(),
            order=milestone_index,
        )
        created_milestones.append(milestone)

        for task_index, task_data in enumerate(milestone_data["tasks"]):
            task = Task.objects.create(
                milestone=milestone,
                title=task_data["title"].strip(),
                description=task_data.get("description", "").strip(),
                priority=task_data.get("priority", "medium"),
                order=task_index,
            )

            for criterion in task_data.get("acceptance_criteria", []):
                AcceptanceCriterion.objects.create(
                    task=task,
                    description=criterion.strip(),
                )

    return created_milestones
