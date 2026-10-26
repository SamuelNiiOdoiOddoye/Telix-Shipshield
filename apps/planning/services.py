from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.assistant.services import validate_project_plan
from apps.planning.models import (
    AcceptanceCriterion,
    Milestone,
    ProjectPlan,
    Task,
)
from apps.projects.models import Project


def save_plan_draft(*, project: Project, user, plan: dict) -> ProjectPlan:
    """Validate and save a draft without creating execution records."""
    if project.owner_id != user.pk:
        raise PermissionDenied(
            "You do not have permission to edit this project's plan."
        )

    validated_plan = validate_project_plan(plan)

    with transaction.atomic():
        draft, _ = ProjectPlan.objects.select_for_update().get_or_create(
            project=project,
            defaults={"plan": validated_plan},
        )

        if draft.status == ProjectPlan.Status.APPROVED:
            raise ValidationError(
                "This plan has already been approved and cannot be edited as a draft."
            )

        draft.plan = validated_plan
        draft.save(update_fields=["plan", "updated_at"])
        return draft


@transaction.atomic
def approve_and_save_plan(
    *, project: Project, user, plan: dict | None = None
) -> list[Milestone]:
    """Approve a saved draft and atomically create its execution records."""
    if project.owner_id != user.pk:
        raise PermissionDenied(
            "You do not have permission to approve this project's plan."
        )

    draft = (
        ProjectPlan.objects.select_for_update()
        .filter(project=project)
        .first()
    )

    if draft is None:
        if plan is None:
            raise ValidationError("Save a valid draft before approving it.")
        validated_plan = validate_project_plan(plan)
        draft = ProjectPlan.objects.create(
            project=project,
            plan=validated_plan,
        )
    else:
        if draft.status == ProjectPlan.Status.APPROVED:
            raise ValidationError("This project plan has already been approved.")
        validated_plan = validate_project_plan(draft.plan)

        if plan is not None:
            validated_plan = validate_project_plan(plan)
            draft.plan = validated_plan

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

    draft.status = ProjectPlan.Status.APPROVED
    draft.approved_by = user
    draft.approved_at = timezone.now()
    draft.save(
        update_fields=[
            "plan",
            "status",
            "approved_by",
            "approved_at",
            "updated_at",
        ]
    )

    return created_milestones