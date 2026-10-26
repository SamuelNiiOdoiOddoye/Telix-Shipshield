from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.evidence.models import Evidence
from apps.planning.models import Task
from apps.projects.models import Project


@login_required
@require_POST
def evidence_add(request, project_id, task_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.pk:
        raise PermissionDenied
    task = get_object_or_404(Task, pk=task_id, milestone__project=project)

    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    url = request.POST.get("url", "").strip()
    evidence_type = request.POST.get("evidence_type", Evidence.EvidenceType.NOTE)
    allowed_types = {value for value, _label in Evidence.EvidenceType.choices}

    if not title:
        messages.error(request, "Evidence needs a title.")
    elif evidence_type not in allowed_types:
        messages.error(request, "Choose a valid evidence type.")
    else:
        Evidence.objects.create(
            task=task,
            submitted_by=request.user,
            title=title,
            description=description,
            url=url,
            evidence_type=evidence_type,
        )
        messages.success(request, f'Evidence saved for “{task.title}”.')

    return redirect("projects:detail", project_id=project.pk)
