from django.contrib import admin
from .models import Batch


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = (
        "batch_name",
        "course",
        "trainer",
        "session",
        "capacity",
        "status",
        "is_active",
    )

    list_filter = (
        "status",
        "session",
        "is_active",
    )

    search_fields = (
        "batch_name",
        "batch_code",
        "trainer",
    )

    ordering = ("-created_at",)