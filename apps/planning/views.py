import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST, require_http_methods

from apps.assistant.services import PlanValidationError
from apps.planning.models import ProjectPlan, Task, Milestone
from apps.planning.services import approve_and_save_plan, save_plan_draft
from apps.projects.models import Project, Risk


def _owned_project_or_403(project_id, user):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != user.pk:
        raise PermissionDenied
    return project


@login_required
def project_detail(request, project_id):
    project = _owned_project_or_403(project_id, request.user)
    draft = ProjectPlan.objects.filter(project=project).first()

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "draft": draft,
            "milestones": project.milestones.prefetch_related(
                "tasks__acceptance_criteria", "tasks__evidence"
            ),
            "milestone_count": project.milestones.count(),
            "completed_milestone_count": project.milestones.filter(is_completed=True).count(),
            "task_count": Task.objects.filter(milestone__project=project).count(),
            "completed_task_count": Task.objects.filter(milestone__project=project, status=Task.Status.DONE).count(),
            "progress_percent": round(
                Task.objects.filter(milestone__project=project, status=Task.Status.DONE).count() * 100
                / Task.objects.filter(milestone__project=project).count()
            ) if Task.objects.filter(milestone__project=project).exists() else 0,
            "task_status_choices": Task.Status.choices,
            "risks": project.risks.all(),
            "risk_status_choices": Risk.Status.choices,
            "risk_severity_choices": Risk.Severity.choices,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def plan_edit(request, project_id):
    project = _owned_project_or_403(project_id, request.user)
    draft = ProjectPlan.objects.filter(project=project).first()

    if request.method == "POST":
        raw_plan = request.POST.get("plan", "").strip()
        try:
            plan = json.loads(raw_plan)
            draft = save_plan_draft(
                project=project,
                user=request.user,
                plan=plan,
            )
        except json.JSONDecodeError:
            return render(
                request,
                "planning/plan_edit.html",
                {
                    "project": project,
                    "draft": draft,
                    "plan_json": raw_plan,
                    "error": "Enter valid JSON.",
                },
                status=400,
            )
        except (PlanValidationError, ValidationError) as exc:
            return render(
                request,
                "planning/plan_edit.html",
                {
                    "project": project,
                    "draft": draft,
                    "plan_json": raw_plan,
                    "error": str(exc),
                },
                status=400,
            )

        return redirect("projects:detail", project_id=project.pk)

    starter_plan = {
        "milestones": [
            {
                "title": "Clarify the outcome",
                "description": "Define the intended result and what success looks like.",
                "tasks": [
                    {
                        "title": "Define success criteria",
                        "description": f"Agree on measurable success for {project.name}.",
                        "priority": "high",
                        "acceptance_criteria": ["Success criteria are documented and agreed"],
                    },
                    {
                        "title": "Identify resources, constraints, and risks",
                        "priority": "medium",
                        "acceptance_criteria": ["Key resources and constraints are recorded"],
                    },
                ],
            },
            {
                "title": "Execute the core work",
                "description": "Deliver the main work required to reach the goal.",
                "tasks": [
                    {
                        "title": "Complete the first delivery increment",
                        "priority": "high",
                        "acceptance_criteria": ["The increment is reviewed against the agreed criteria"],
                    },
                ],
            },
            {
                "title": "Verify and deliver",
                "description": "Review results, collect evidence, and prepare handover.",
                "tasks": [
                    {
                        "title": "Review results and capture evidence",
                        "priority": "high",
                        "acceptance_criteria": ["Delivery evidence and remaining gaps are documented"],
                    },
                ],
            },
        ]
    }
    plan_json = json.dumps(draft.plan if draft else starter_plan, indent=2)
    return render(
        request,
        "planning/plan_edit.html",
        {
            "project": project,
            "draft": draft,
            "plan_json": plan_json,
        },
    )


@login_required
@require_POST
def plan_approve(request, project_id):
    project = _owned_project_or_403(project_id, request.user)
    try:
        approve_and_save_plan(project=project, user=request.user)
    except (PlanValidationError, ValidationError) as exc:
        draft = ProjectPlan.objects.filter(project=project).first()
        return render(
            request,
            "projects/project_detail.html",
            {
                "project": project,
                "draft": draft,
                "milestones": project.milestones.prefetch_related(
                    "tasks__acceptance_criteria", "tasks__evidence"
                ),
                "milestone_count": project.milestones.count(),
                "completed_milestone_count": project.milestones.filter(is_completed=True).count(),
                "task_count": Task.objects.filter(milestone__project=project).count(),
                "completed_task_count": Task.objects.filter(milestone__project=project, status=Task.Status.DONE).count(),
                "progress_percent": 0,
                "task_status_choices": Task.Status.choices,
                "risks": project.risks.all(),
                "risk_status_choices": Risk.Status.choices,
                "risk_severity_choices": Risk.Severity.choices,
                "error": str(exc),
            },
            status=400,
        )

    return redirect("projects:detail", project_id=project.pk)

@login_required
@require_POST
def task_update(request, project_id, task_id):
    project = _owned_project_or_403(project_id, request.user)
    task = get_object_or_404(Task, pk=task_id, milestone__project=project)
    status = request.POST.get("status", "")
    valid_statuses = {value for value, _label in Task.Status.choices}
    if status not in valid_statuses:
        messages.error(request, "Choose a valid task status.")
        return redirect("projects:detail", project_id=project.pk)

    with transaction.atomic():
        task.status = status
        task.save(update_fields=["status", "updated_at"])
        milestone = task.milestone
        if milestone:
            milestone.is_completed = not milestone.tasks.exclude(status=Task.Status.DONE).exists()
            milestone.save(update_fields=["is_completed", "updated_at"])
        all_tasks = Task.objects.filter(milestone__project=project)
        if all_tasks.exists() and not all_tasks.exclude(status=Task.Status.DONE).exists():
            project.status = Project.Status.COMPLETED
        elif project.status == Project.Status.DRAFT or project.status == Project.Status.COMPLETED:
            project.status = Project.Status.ACTIVE
        project.save(update_fields=["status", "updated_at"])
    messages.success(request, f'Task status updated: {task.title}.')
    return redirect("projects:detail", project_id=project.pk)
