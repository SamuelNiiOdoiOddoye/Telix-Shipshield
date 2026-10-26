from django.urls import path

from apps.evidence import views

app_name = "evidence"

urlpatterns = [
    path("projects/<uuid:project_id>/tasks/<uuid:task_id>/add/", views.evidence_add, name="add"),
]
