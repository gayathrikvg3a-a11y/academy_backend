from django.db import models


class InternshipStudent(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    internship_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    student_name = models.CharField(
        max_length=200,
    )

    phone = models.CharField(
        max_length=20,
    )

    email = models.EmailField()

    college = models.CharField(
        max_length=200,
    )

    academic_stream = models.CharField(
        max_length=100,
    )

    internship_title = models.CharField(
        max_length=200,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    certificate = models.FileField(
        upload_to="internships/certificates/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE",
    )

    is_active = models.BooleanField(
        default=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]
        verbose_name = "Internship Student"
        verbose_name_plural = "Internship Students"

    def save(self, *args, **kwargs):

        if not self.internship_id:

            last_student = (
                InternshipStudent.objects
                .order_by("-id")
                .first()
            )

            if last_student:
                next_number = last_student.id + 1
            else:
                next_number = 1

            self.internship_id = (
                f"INT{next_number:05d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.internship_id} - "
            f"{self.student_name}"
        )


class Vacancy(models.Model):

    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    INTERNSHIP = "INTERNSHIP"
    CONTRACT = "CONTRACT"

    JOB_TYPES = (
        (FULL_TIME, "Full Time"),
        (PART_TIME, "Part Time"),
        (INTERNSHIP, "Internship"),
        (CONTRACT, "Contract"),
    )
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=150,blank=True)
    location = models.CharField(max_length=150)
    job_type = models.CharField(max_length=20,choices=JOB_TYPES,default=FULL_TIME,)
    experience = models.CharField(max_length=100,blank=True,help_text="Example: 2-4 Years")
    vacancies = models.PositiveIntegerField(default=1)
    salary = models.CharField(max_length=100,blank=True,help_text="Example: ₹25,000 - ₹35,000")
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    close_date = models.DateField(blank=True,null=True,help_text="Last date to apply.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "display_order",
            "-created_at",
        ]

        verbose_name = "Vacancy"
        verbose_name_plural = "Vacancies"

    def __str__(self):
        return self.title