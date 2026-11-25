from rest_framework import serializers
from .models import Batch


class BatchSerializer(serializers.ModelSerializer):

    course_name = serializers.CharField(
        source="course.name",
        read_only=True
    )

    class Meta:
        model = Batch
        fields = [
            "id",
            "batch_name",
            "batch_code",
            "course",
            "course_name",
            "trainer",
            "session",
            "capacity",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "description",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]