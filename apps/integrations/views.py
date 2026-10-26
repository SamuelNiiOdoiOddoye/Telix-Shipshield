
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.projects.models import Project
from apps.integrations.models import Repository, AuditRun
from apps.integrations.services import (
    GitHubIntegrationError,
    inspect_repository,
    parse_github_url,
)


def _owned_project(project_id, user):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner_id != user.pk:
        raise PermissionDenied

    return project


@login_required
def repository_connect(request, project_id):
    project = _owned_project(project_id, request.user)
    error = None

    if request.method == "POST":
        repository_url = request.POST.get("repository_url", "").strip()

        try:
            owner, name = parse_github_url(repository_url)
            details = inspect_repository(owner, name)

            repository, _ = Repository.objects.update_or_create(
                project=project,
                repository_url=details["html_url"],
                defaults={
                    "provider": "github",
                    "owner_name": owner,
                    "repository_name": name,
                    "default_branch": details["default_branch"],
                    "is_active": True,
                    "connected_by": request.user,
                },
            )

            return redirect(
                "integrations:repository_detail",
                project_id=project.pk,
                repository_id=repository.pk,
            )

        except GitHubIntegrationError as exc:
            error = str(exc)

    return render(
        request,
        "integrations/repository_connect.html",
        {"project": project, "error": error},
    )


@login_required
def repository_detail(request, project_id, repository_id):
    project = _owned_project(project_id, request.user)

    repository = get_object_or_404(
        Repository,
        pk=repository_id,
        project=project,
        is_active=True,
    )

    latest_audit = repository.audit_runs.first()

    return render(
        request,
        "integrations/repository_detail.html",
        {
            "project": project,
            "repository": repository,
            "latest_audit": latest_audit,
        },
    )


@login_required
@require_POST
def repository_audit(request, project_id, repository_id):
    project = _owned_project(project_id, request.user)

    repository = get_object_or_404(
        Repository,
        pk=repository_id,
        project=project,
        is_active=True,
    )

    audit = AuditRun.objects.create(
        repository=repository,
        status=AuditRun.Status.RUNNING,
    )

    try:
        owner, name = parse_github_url(repository.repository_url)
        details = inspect_repository(owner, name)

        findings = [
            {
                "type": "repository",
                "message": (
                    f"Repository is accessible: {details['full_name']}."
                ),
            },
            {
                "type": "branch",
                "message": (
                    f"Default branch: {details['default_branch'] or 'Unknown'}."
                ),
            },
            {
                "type": "readme",
                "message": (
                    "README found."
                    if details["readme"]
                    else "README could not be retrieved or is missing."
                ),
            },
            {
                "type": "files",
                "message": (
                    f"Found {len(details['root_files'])} root-level entries."
                ),
            },
        ]

        audit.status = AuditRun.Status.COMPLETED
        audit.commit_sha = details["latest_commit_sha"]
        audit.summary = (
            f"Read-only inspection of {details['full_name']}. "
            f"Found {len(details['root_files'])} root-level entries."
        )
        audit.findings = findings
        audit.save()

        repository.default_branch = details["default_branch"]
        repository.save(update_fields=["default_branch", "updated_at"])

    except GitHubIntegrationError as exc:
        audit.status = AuditRun.Status.FAILED
        audit.summary = str(exc)
        audit.save(update_fields=["status", "summary"])

    return redirect(
        "integrations:repository_detail",
        project_id=project.pk,
        repository_id=repository.pk,
    )
