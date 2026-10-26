import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods

from apps.assistant.services import PlanValidationError
from apps.planning.models import ProjectPlan
from apps.planning.services import approve_and_save_plan, save_plan_draft
from apps.projects.models import Project


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
                "tasks__acceptance_criteria"
            ),
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

    plan_json = json.dumps(
        draft.plan if draft else {"milestones": []},
        indent=2,
    )
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
                    "tasks__acceptance_criteria"
                ),
                "error": str(exc),
            },
            status=400,
        )

    return redirect("projects:detail", project_id=project.pk)