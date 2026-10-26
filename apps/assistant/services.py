from typing import Any
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

