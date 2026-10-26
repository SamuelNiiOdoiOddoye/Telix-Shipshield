
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        lambda request: redirect("projects:dashboard"),
        name="home",
    ),
    path("projects/", include("apps.projects.urls")),
    path("", include("apps.planning.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("integrations/", include("apps.integrations.urls")),
]
