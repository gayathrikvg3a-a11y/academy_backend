from django.db import models
from courses.models import Course


class Batch(models.Model):
    class SessionChoices(models.TextChoices):
        MORNING = "MORNING", "Morning"
        EVENING = "EVENING", "Evening"

    class StatusChoices(models.TextChoices):
        UPCOMING = "UPCOMING", "Upcoming"
        ONGOING = "ONGOING", "Ongoing"
        COMPLETED = "COMPLETED", "Completed"

    batch_name = models.CharField(
        max_length=100,
        unique=True
    )

    batch_code = models.CharField(
        max_length=20,
        unique=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="batches"
    )

    trainer = models.CharField(
        max_length=100
    )

    session = models.CharField(
        max_length=10,
        choices=SessionChoices.choices
    )

    capacity = models.PositiveIntegerField(
        default=30
    )

    start_date = models.DateField()

    end_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.UPCOMING
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Batch"
        verbose_name_plural = "Batches"

    def __str__(self):
        return f"{self.batch_name} ({self.course.name})"