from django.urls import path

from apps.planning import views

app_name = "planning"

urlpatterns = [
    path(
        "projects/<uuid:project_id>/plan/",
        views.plan_edit,
        name="plan_edit",
    ),
    path(
        "projects/<uuid:project_id>/plan/approve/",
        views.plan_approve,
        name="plan_approve",
    ),
]