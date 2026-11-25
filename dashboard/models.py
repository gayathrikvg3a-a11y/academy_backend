from django.db import models

# Create your models here.
class Permission(models.Model):
    permission_name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["permission_name"]

    def __str__(self):
        return self.permission_name


class Role(models.Model):
    role_name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["role_name"]

    def __str__(self):
        return self.role_name


