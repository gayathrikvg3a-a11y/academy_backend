from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class Enquiry(models.Model):

    STAGE_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('FOLLOW_UP', 'Follow Up'),
        ('INTERESTED', 'Interested'),
        ('CONVERTED', 'Converted'),
        ('NOT_INTERESTED', 'Not Interested'),
    ]

    student_name = models.CharField(max_length=200)

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        related_name='enquiries'
    )

    college = models.CharField(
        max_length=200,
        blank=True
    )

    academic_stream = models.CharField(
    max_length=200,
    blank=True
    )

    recommended_by = models.CharField(
        max_length=200,
        blank=True
    )

    enquiry_stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default='NEW'
    )

    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_enquiries'
    )

    feedback = models.TextField(blank=True)

    is_converted = models.BooleanField(default=False)

    enquiry_date = models.DateField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_name


class CallHistory(models.Model):

    CALL_STATUS_CHOICES = [
        ('ANSWERED', 'Answered'),
        ('NO_ANSWER', 'No Answer'),
        ('BUSY', 'Busy'),
        ('SWITCHED_OFF', 'Switched Off'),
        ('CALL_BACK', 'Call Back'),
    ]

    enquiry = models.ForeignKey(
        Enquiry,
        on_delete=models.CASCADE,
        related_name='call_history'
    )

    called_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    call_status = models.CharField(
        max_length=30,
        choices=CALL_STATUS_CHOICES
    )

    feedback = models.TextField(blank=True)

    call_date = models.DateTimeField(auto_now_add=True)

    next_follow_up_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.enquiry.student_name} - {self.call_status}"


class EnquiryNew(models.Model):

    ENQUIRY_TYPE_CHOICES = [
        ("COURSE", "Course"),
        ("INTERNSHIP", "Internship"),
    ]

    STAGE_CHOICES = [
        ("NEW", "New"),
        ("CONTACTED", "Contacted"),
        ("FOLLOW_UP", "Follow Up"),
        ("INTERESTED", "Interested"),
        ("CONVERTED", "Converted"),
        ("NOT_INTERESTED", "Not Interested"),
    ]

    enquiry_type = models.CharField(
        max_length=20,
        choices=ENQUIRY_TYPE_CHOICES,
        default="COURSE"
    )

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=200)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="new_enquiries"
    )

    message = models.TextField()

    # CRM fields
    status = models.CharField(
        max_length=20,
        choices=STAGE_CHOICES,
        default="NEW"
    )
    feedback = models.TextField(blank=True)
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enquiry_responsible_person"
    )
    recommended_by = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Testimonial(models.Model):

    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=100)
    note = models.TextField()
    url = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name