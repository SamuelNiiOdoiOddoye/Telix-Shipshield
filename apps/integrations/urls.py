
from django.urls import path

from apps.integrations import views

app_name = "integrations"

urlpatterns = [
    path(
        "projects/<uuid:project_id>/repository/connect/",
        views.repository_connect,
        name="repository_connect",
    ),
    path(
        "projects/<uuid:project_id>/repository/<uuid:repository_id>/",
        views.repository_detail,
        name="repository_detail",
    ),
    path(
        "projects/<uuid:project_id>/repository/<uuid:repository_id>/audit/",
        views.repository_audit,
        name="repository_audit",
    ),
]
