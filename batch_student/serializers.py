from rest_framework import serializers

from .models import BatchStudent


class BatchStudentSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(
        source="batch.batch_name",
        read_only=True,
    )

    student_name = serializers.CharField(
        source="student.student_name",
        read_only=True,
    )

    class Meta:
        model = BatchStudent
        fields = [
            "id",
            "batch",
            "batch_name",
            "student",
            "student_name",
            "roll_number",
            "admission_date",
            "status",
            "remarks",
            "created_at",
            "updated_at",
        ]