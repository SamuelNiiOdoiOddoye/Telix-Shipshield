from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from apps.projects.models import Project


@login_required
def dashboard(request):
    projects = Project.objects.filter(owner=request.user)

    return render(
        request,
        "projects/dashboard.html",
        {"projects": projects},
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
                {"error": "Project name is required."},
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

        return redirect("projects:dashboard")

    return render(request, "projects/project_form.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("projects:dashboard")

    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:dashboard")

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )
    if request.user.is_authenticated:
        return redirect("projects:dashboard")
    
    form = UserCreationForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request,user)
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/signup.html",
        {"form": form},
    )
