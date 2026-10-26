
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone

from apps.projects.models import Project
from apps.integrations.models import Repository, AuditRun
from apps.integrations.services import (
    GitHubIntegrationError,
    inspect_repository,
    parse_github_url,
)

import re


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

def build_health_findings(details):
    """Produce evidence-backed checks from the data we actually inspected."""
    entries = details.get("root_files", [])
    root_by_name = {
        item.get("name", "").lower(): item
        for item in entries
        if item.get("name")
    }
    root_names = set(root_by_name)
    readme = details.get("readme", "") or ""
    findings = []

    def add_finding(
        check_id,
        category,
        check,
        status,
        severity,
        summary,
        evidence,
        recommendation="",
    ):
        findings.append({
            "id": check_id,
            "category": category,
            "check": check,
            "status": status,
            "severity": severity,
            "summary": summary,
            "evidence": evidence,
            "recommendation": recommendation,
        })

    # 1. Repository metadata
    repo_name = details.get("full_name", "Unknown repository")
    branch = details.get("default_branch", "")
    commit_sha = details.get("latest_commit_sha", "")

    add_finding(
        "repository_access",
        "Repository",
        "Repository access",
        "passed" if details.get("html_url") else "unverified",
        "info",
        (
            f"GitHub returned repository metadata for {repo_name}."
            if details.get("html_url")
            else "Repository metadata was incomplete."
        ),
        [{
            "source_path": details.get("html_url") or "GitHub repository API",
            "detail": f"Repository: {repo_name}",
        }],
    )

    add_finding(
        "default_branch",
        "Version control",
        "Default branch",
        "passed" if branch else "unverified",
        "info",
        (
            f"The configured default branch is {branch}."
            if branch
            else "The default branch could not be confirmed."
        ),
        [{
            "source_path": "GitHub repository metadata",
            "detail": f"Default branch: {branch or 'Not returned'}",
        }],
    )

    add_finding(
        "latest_commit",
        "Version control",
        "Latest commit",
        "passed" if commit_sha else "unverified",
        "info",
        (
            "GitHub returned a latest commit reference."
            if commit_sha
            else "A latest commit reference was not returned."
        ),
        [{
            "source_path": f"{details.get('html_url', '')}/commits",
            "detail": f"Commit SHA: {commit_sha or 'Not returned'}",
        }],
    )

    # 2. README presence and documentation signals
    readme_names = {
        "readme", "readme.md", "readme.rst", "readme.txt",
    }
    found_readme = sorted(readme_names.intersection(root_names))

    if not found_readme:
        add_finding(
            "readme_presence",
            "Documentation",
            "README presence",
            "failed",
            "high",
            "No recognized README file was found among the repository root entries.",
            [{
                "source_path": "Repository root listing",
                "detail": "Checked for README, README.md, README.rst, and README.txt.",
            }],
            "Add a README that explains the project's purpose, setup, usage, and testing.",
        )
    elif not readme.strip():
        add_finding(
            "readme_presence",
            "Documentation",
            "README content",
            "unverified",
            "medium",
            "A README file is listed, but its content was not available to the audit.",
            [{
                "source_path": found_readme[0],
                "detail": "The file appeared in the root listing; readable content was unavailable.",
            }],
            "Retry the inspection to retrieve and review the README content.",
        )
    else:
        add_finding(
            "readme_presence",
            "Documentation",
            "README presence",
            "passed",
            "info",
            f"README content was retrieved from {found_readme[0]}.",
            [{
                "source_path": found_readme[0],
                "detail": f"Retrieved {len(readme)} characters (content may be truncated).",
            }],
        )

        documentation_sections = [
            {
                "id": "readme_setup",
                "name": "Installation and setup instructions",
                "pattern": r"installation|getting started|setup|set up|prerequisites",
                "recommendation": (
                    "Document prerequisites, installation steps, environment "
                    "configuration, and how to start the project."
                ),
            },
            {
                "id": "readme_usage",
                "name": "Usage instructions",
                "pattern": r"usage|how to use|running the|quick start|quickstart",
                "recommendation": (
                    "Add examples showing how to run or use the project."
                ),
            },
            {
                "id": "readme_testing",
                "name": "Testing instructions",
                "pattern": r"testing|tests|test suite|running tests",
                "recommendation": (
                    "Document the test command and how to interpret its results."
                ),
            },
        ]

        for section in documentation_sections:
            present = bool(
                re.search(
                    rf"(?im)^\s*#{{1,6}}\s+.*(?:{section['pattern']})",
                    readme,
                )
            )

            add_finding(
                section["id"],
                "Documentation",
                section["name"],
                "passed" if present else "failed",
                "info" if present else "medium",
                (
                    f"README contains a heading for {section['name'].lower()}."
                    if present
                    else f"No recognizable README heading for {section['name'].lower()} was found."
                ),
                [{
                    "source_path": found_readme[0],
                    "detail": (
                        "Checked retrieved README headings using keyword matching."
                    ),
                }],
                "" if present else section["recommendation"],
            )

    # 3. Dependency manifest indicators
    manifest_names = {
        "requirements.txt",
        "pyproject.toml",
        "pipfile",
        "pipfile.lock",
        "poetry.lock",
        "package.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "pubspec.yaml",
        "go.mod",
        "cargo.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "composer.json",
    }
    found_manifests = sorted(manifest_names.intersection(root_names))

    add_finding(
        "dependency_manifest",
        "Development health",
        "Dependency manifest",
        "passed" if found_manifests else "unverified",
        "info" if found_manifests else "medium",
        (
            "Found dependency/build manifest(s): "
            + ", ".join(found_manifests)
            if found_manifests
            else "No recognized dependency or build manifest was detected at the repository root."
        ),
        [{
            "source_path": "Repository root listing",
            "detail": (
                ", ".join(found_manifests)
                if found_manifests
                else "Only root entries were checked; manifests may exist in subdirectories or this may not be a software project."
            ),
        }],
        (
            ""
            if found_manifests
            else "If this is a software project, confirm how dependencies and build steps are declared."
        ),
    )

    # 4. Test indicators
    test_names = [
        name for name in root_names
        if name in {"tests", "test", "__tests__"}
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name in {"pytest.ini", "tox.ini"}
    ]
    has_test_directory = any(
        root_by_name[name].get("type") == "dir"
        for name in test_names
        if name in root_by_name
    )
    has_test_file = any(
        root_by_name[name].get("type") == "file"
        for name in test_names
        if name in root_by_name
    )

    if has_test_directory or has_test_file:
        test_status = "passed"
        test_severity = "info"
        test_summary = (
            "A likely test directory or test-related file was detected at the root."
        )
        test_recommendation = (
            "Run the test suite and record the command, result, and commit as verification evidence."
        )
    else:
        test_status = "unverified"
        test_severity = "medium"
        test_summary = (
            "No obvious test indicator was detected among the root entries. "
            "Nested test directories and test execution were not checked."
        )
        test_recommendation = (
            "Inspect the full repository tree and identify the test suite. "
            "If tests do not exist, add tests for critical behavior."
        )

    add_finding(
        "test_presence",
        "Development health",
        "Test suite indicators",
        test_status,
        test_severity,
        test_summary,
        [{
            "source_path": "Repository root listing",
            "detail": (
                ", ".join(test_names)
                if test_names
                else "No matching test-related root entry was detected."
            ),
        }],
        test_recommendation,
    )

    # 5. Continuous integration indicators
    ci_names = {
        ".github",
        ".gitlab-ci.yml",
        ".circleci",
        "azure-pipelines.yml",
        "jenkinsfile",
        "bitbucket-pipelines.yml",
    }
    found_ci = sorted(ci_names.intersection(root_names))

    if found_ci:
        ci_status = "passed"
        ci_severity = "info"
        ci_summary = (
            "A possible CI configuration location or file was detected at the root."
        )
        ci_recommendation = (
            "Inspect the configuration and confirm that workflows run successfully "
            "for the default branch."
        )
    else:
        ci_status = "unverified"
        ci_severity = "low"
        ci_summary = (
            "No recognized CI indicator was detected among the root entries. "
            "External CI services and nested configuration were not checked."
        )
        ci_recommendation = (
            "If automated verification is needed, configure CI to run tests and "
            "basic quality checks on changes."
        )

    add_finding(
        "ci_presence",
        "Development health",
        "Continuous integration indicators",
        ci_status,
        ci_severity,
        ci_summary,
        [{
            "source_path": "Repository root listing",
            "detail": (
                ", ".join(found_ci)
                if found_ci
                else "No recognized CI root entry was detected."
            ),
        }],
        ci_recommendation,
    )

    return findings


@login_required
@require_POST

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
        started_at=timezone.now(),
    )

    try:
        owner, name = parse_github_url(repository.repository_url)
        details = inspect_repository(owner, name)
        findings = build_health_findings(details)

        passed_count = sum(
            finding["status"] == "passed" for finding in findings
        )
        failed_count = sum(
            finding["status"] == "failed" for finding in findings
        )
        unverified_count = sum(
            finding["status"] == "unverified" for finding in findings
        )

        audit.status = AuditRun.Status.COMPLETED
        audit.commit_sha = details.get("latest_commit_sha", "")
        audit.summary = (
            f"Health audit completed for {details.get('full_name', repository)}. "
            f"{passed_count} passed, {failed_count} failed, "
            f"{unverified_count} unverified. "
            "Checks are based on repository metadata, root entries, "
            "and retrieved README content; tests were not executed."
        )
        audit.findings = findings
        audit.completed_at = timezone.now()
        audit.save(
            update_fields=[
                "status",
                "commit_sha",
                "summary",
                "findings",
                "completed_at",
            ]
        )

        new_default_branch = details.get("default_branch", "")
        if new_default_branch != repository.default_branch:
            repository.default_branch = new_default_branch
            repository.save(update_fields=["default_branch", "updated_at"])

    except GitHubIntegrationError as exc:
        audit.status = AuditRun.Status.FAILED
        audit.summary = str(exc)
        audit.completed_at = timezone.now()
        audit.save(
            update_fields=["status", "summary", "completed_at"]
        )

    return redirect(
        "integrations:repository_detail",
        project_id=project.pk,
        repository_id=repository.pk,
    )
