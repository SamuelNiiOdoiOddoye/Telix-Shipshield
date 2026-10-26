
from django.urls import path

from apps.projects import views
from apps.planning.views import project_detail

app_name = "projects"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.project_create, name="create"),
    path("<uuid:project_id>/", project_detail, name="detail")
]
