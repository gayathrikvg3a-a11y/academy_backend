"""
URL configuration for cignes_academy_main project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("enquiries.urls")),
    path("api/", include("courses.urls")),
    path("api/", include("students.urls")),
    path("api/", include("batch.urls")),
    path("api/", include("batch_student.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("events.urls")),
    path("api/", include("gallery.urls")),
    path("api/", include("internships.urls")),
    path("api/", include("dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )