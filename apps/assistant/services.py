from django.db import transaction
from typing import Any

from apps.planning.models import(
    AcceptanceCriterion,
    Milestone,
    Task,
)
class PlanValidationError(ValueError):
    """Raised when a generated project plan is invalid."""


def validate_project_plan(plan: Any) -> dict:
    """
    Validate a proposed project plan before it can be shown for approval.

    Expected structure:
    {
        "milestones": [
            {
                "title": "...",
                "tasks": [
                    {
                        "title": "...",
                        "priority": "low|medium|high|critical",
                        "acceptance_criteria": ["..."]
                    }
                ]
            }
        ]
    }
    """
    if not isinstance(plan, dict):
        raise PlanValidationError("The plan must be a JSON object.")

    milestones = plan.get("milestones")

    if not isinstance(milestones, list) or not milestones:
        raise PlanValidationError(
            "The plan must contain at least one milestone."
        )

    allowed_priorities = {"low", "medium", "high", "critical"}

    for milestone_index, milestone in enumerate(milestones, start=1):
        if not isinstance(milestone, dict):
            raise PlanValidationError(
                f"Milestone {milestone_index} must be an object."
            )

        title = milestone.get("title")
        if not isinstance(title, str) or not title.strip():
            raise PlanValidationError(
                f"Milestone {milestone_index} needs a title."
            )

        tasks = milestone.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            raise PlanValidationError(
                f"Milestone {milestone_index} needs at least one task."
            )

        for task_index, task in enumerate(tasks, start=1):
            if not isinstance(task, dict):
                raise PlanValidationError(
                    f"Task {task_index} in milestone "
                    f"{milestone_index} must be an object."
                )

            task_title = task.get("title")
            if not isinstance(task_title, str) or not task_title.strip():
                raise PlanValidationError(
                    f"Task {task_index} in milestone "
                    f"{milestone_index} needs a title."
                )

            priority = task.get("priority", "medium")
            if priority not in allowed_priorities:
                raise PlanValidationError(
                    f"Task '{task_title}' has an invalid priority."
                )

            criteria = task.get("acceptance_criteria", [])
            if not isinstance(criteria, list) or not all(
                isinstance(item, str) and item.strip()
                for item in criteria
            ):
                raise PlanValidationError(
                    f"Task '{task_title}' has invalid acceptance criteria."
                )

    return plan

@transaction.atomic
def approve_and_save_plan(project, plan):
    """
    Validate and persist an explicitly approved project plan.

    If any database write fails, all changes are rolled back.
    """
    validated_plan = validate_project_plan(plan)

    for milestone_order, milestone_data in enumerate(
        validated_plan["milestones"]
    ):
        milestone = Milestone.objects.create(
            project=project,
            title=milestone_data["title"].strip(),
            description=milestone_data.get("description", "").strip(),
            order=milestone_order,
        )

        for task_order, task_data in enumerate(
            milestone_data["tasks"]
        ):
            task = Task.objects.create(
                milestone=milestone,
                title=task_data["title"].strip(),
                description=task_data.get("description", "").strip(),
                priority=task_data.get("priority", "medium"),
                order=task_order,
            )

            criteria = task_data.get("acceptance_criteria", [])

            AcceptanceCriterion.objects.bulk_create([
                AcceptanceCriterion(
                    task=task,
                    description=criterion.strip(),
                )
                for criterion in criteria
            ])

    return {
        "milestones_created": len(validated_plan["milestones"]),
        "tasks_created": sum(
            len(milestone["tasks"])
            for milestone in validated_plan["milestones"]
        ),
    }
