from django.urls import path

from apps.projects import views
from apps.planning.views import project_detail

app_name = "projects"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.project_create, name="create"),
    path("register/", views.register, name="register"),
    path("<uuid:project_id>/risks/add/", views.risk_add, name="risk_add"),
    path("<uuid:project_id>/risks/<uuid:risk_id>/update/", views.risk_update, name="risk_update"),
    path("<uuid:project_id>/", project_detail, name="detail"),
]
