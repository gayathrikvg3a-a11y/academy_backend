from django.db import models
from batch.models import Batch
from students.models import Student


class BatchStudent(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        DROPPED = "DROPPED", "Dropped"

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="batch_students"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="batch_students"
    )

    roll_number = models.PositiveIntegerField()

    admission_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["roll_number"]

        constraints = [
            models.UniqueConstraint(
                fields=["batch", "student"],
                name="unique_student_per_batch"
            ),
            models.UniqueConstraint(
                fields=["batch", "roll_number"],
                name="unique_roll_per_batch"
            )
        ]

    def __str__(self):
        return f"{self.student.student_name} - {self.batch.batch_name}"