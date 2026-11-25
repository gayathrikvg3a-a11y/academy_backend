from django.db import models


class Event(models.Model):
    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    banner = models.ImageField(
        upload_to="events/banners/",
        null=True,
        blank=True
    )

    event_date = models.DateField()

    event_time = models.TimeField(
        null=True,
        blank=True
    )

    venue = models.CharField(
        max_length=255
    )

    registration_link = models.URLField(
        blank=True
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
        ordering = ["event_date", "event_time"]

    def __str__(self):
        return self.title



class Announcement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_important = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "-published_at"
        ]

    def __str__(self):
        return self.title