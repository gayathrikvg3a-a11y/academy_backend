from django.contrib import admin
from .models import BatchStudent


@admin.register(BatchStudent)
class BatchStudentAdmin(admin.ModelAdmin):
    list_display = (
        "roll_number",
        "student",
        "batch",
        "status",
        "admission_date",
    )

    list_filter = (
        "batch",
        "status",
    )

    search_fields = (
        "student__full_name",
        "batch__batch_name",
    )

    ordering = ("batch", "roll_number")