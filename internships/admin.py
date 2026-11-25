from django.contrib import admin
from .models import InternshipStudent


@admin.register(InternshipStudent)
class InternshipStudentAdmin(admin.ModelAdmin):
    list_display = (
        "internship_id",
        "student_name",
        "phone",
        "college",
        "internship_title",
        "fee",
        "status",
        "is_active",
    )

    search_fields = (
        "internship_id",
        "student_name",
        "phone",
        "email",
        "college",
    )

    list_filter = (
        "status",
        "is_active",
        "start_date",
        "end_date",
    )

    readonly_fields = (
        "internship_id",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)