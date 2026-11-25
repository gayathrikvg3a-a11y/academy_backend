from rest_framework import serializers
from .models import InternshipStudent, Vacancy


class InternshipStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipStudent
        fields = "__all__"
        read_only_fields = (
            "internship_id",
            "created_at",
            "updated_at",
        )



class VacancySerializer(serializers.ModelSerializer):

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "title",
            "department",
            "location",
            "job_type",
            "experience",
            "vacancies",
            "salary",
            "description",
            "responsibilities",
            "requirements",
            "close_date", 
            "is_active",
            "display_order",
            "created_at",
            "updated_at",
        ]

        read_only_fields = (
            "created_at",
            "updated_at",
        )