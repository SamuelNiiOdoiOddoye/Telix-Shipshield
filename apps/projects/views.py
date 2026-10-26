from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.projects.models import Project, Risk


@login_required
def dashboard(request):
    projects = list(
        Project.objects.filter(owner=request.user)
        .annotate(
            total_tasks=Count("milestones__tasks", distinct=True),
            completed_tasks=Count(
                "milestones__tasks",
                filter=Q(milestones__tasks__status="done"),
                distinct=True,
            ),
        )
    )
    for project in projects:
        project.progress_percent = round(
            project.completed_tasks * 100 / project.total_tasks
        ) if project.total_tasks else 0

    return render(
        request,
        "projects/dashboard.html",
        {
            "projects": projects,
            "active_count": sum(
                project.status == Project.Status.ACTIVE for project in projects
            ),
            "task_count": sum(project.total_tasks for project in projects),
            "completed_task_count": sum(
                project.completed_tasks for project in projects
            ),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def project_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        project_type = request.POST.get("project_type", "other")
        goal = request.POST.get("goal", "").strip()
        target_date = request.POST.get("target_date") or None
        valid_types = {choice[0] for choice in Project.ProjectType.choices}

        if not name:
            return render(
                request,
                "projects/project_form.html",
                {"error": "Project name is required.", "project_types": Project.ProjectType.choices},
            )
        if project_type not in valid_types:
            project_type = "other"

        project = Project.objects.create(
            owner=request.user,
            name=name,
            description=description,
            project_type=project_type,
            goal=goal,
            target_date=target_date,
        )
        messages.success(request, f'Project “{project.name}” created. Next, shape its execution plan.')
        return redirect("projects:detail", project_id=project.pk)

    return render(
        request,
        "projects/project_form.html",
        {"project_types": Project.ProjectType.choices},
    )


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("projects:dashboard")

    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to Telix ShipShield. Create your first project to get started.")
        return redirect("projects:dashboard")

    return render(request, "registration/register.html", {"form": form})


@login_required
@require_http_methods(["POST"])
def risk_add(request, project_id):
    from django.core.exceptions import PermissionDenied
    from django.shortcuts import get_object_or_404

    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.pk:
        raise PermissionDenied

    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    mitigation = request.POST.get("mitigation", "").strip()
    severity = request.POST.get("severity", Risk.Severity.MEDIUM)
    valid_severities = {value for value, _label in Risk.Severity.choices}
    if not title:
        messages.error(request, "A risk needs a title.")
    elif severity not in valid_severities:
        messages.error(request, "Choose a valid risk severity.")
    else:
        Risk.objects.create(
            project=project, title=title, description=description,
            mitigation=mitigation, severity=severity, created_by=request.user,
        )
        messages.success(request, f'Risk recorded: {title}.')
    return redirect("projects:detail", project_id=project.pk)


@login_required
@require_http_methods(["POST"])
def risk_update(request, project_id, risk_id):
    from django.core.exceptions import PermissionDenied
    from django.shortcuts import get_object_or_404

    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.pk:
        raise PermissionDenied
    risk = get_object_or_404(Risk, pk=risk_id, project=project)
    status = request.POST.get("status", "")
    valid_statuses = {value for value, _label in Risk.Status.choices}
    if status not in valid_statuses:
        messages.error(request, "Choose a valid risk status.")
    else:
        risk.status = status
        risk.save(update_fields=["status", "updated_at"])
        messages.success(request, f'Risk updated: {risk.title}.')
    return redirect("projects:detail", project_id=project.pk)
