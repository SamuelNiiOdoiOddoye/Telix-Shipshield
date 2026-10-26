
from django.urls import path

from apps.projects import views

app_name = "projects"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.project_create, name="create"),
]
