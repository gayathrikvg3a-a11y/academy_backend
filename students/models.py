
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from courses.models import Course, CourseFeeOption
from enquiries.models import Enquiry
from masters.models import FeeType
from batch.models import Batch
from dashboard.models import Role


# ==========================================================
# STUDENT MODEL
# ==========================================================

class Student(models.Model):

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped'),
        ('ON_HOLD', 'On Hold'),
    ]

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    FEE_TYPE_CHOICES = [
        ('SCHOLARSHIP', 'Scholarship'),
        ('NORMAL_FEE', 'Normal Fee'),
        ('OTHERS', 'Others'),
    ]

    student_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile"
    )

    student_name = models.CharField(max_length=200)

    student_photo = models.ImageField(
        upload_to='students/photos/',
        null=True,
        blank=True
    )

    phone = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    college = models.CharField(max_length=200, blank=True)
    academic_stream = models.CharField(max_length=200, blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students'
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="students",
        null=True,
        blank=True
    )

    fee_type = models.ForeignKey(
        FeeType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    roll_number = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    joining_date = models.DateField(
        null=True,
        blank=True
    )

    remarks = models.TextField(blank=True)

    course_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    fee_option = models.ForeignKey(
        CourseFeeOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )

    discounted_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=True
    )

    recommended_by = models.CharField(
        max_length=200,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    enquiry = models.OneToOneField(
        Enquiry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='converted_student'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_name']
        constraints = [
            models.UniqueConstraint(
                fields=['batch', 'roll_number'],
                name='unique_roll_number_per_batch'
            )
        ]

    def save(self, *args, **kwargs):

        if not self.student_id:

            prefix = "CGA26-"

            last_student = Student.objects.filter(
                student_id__startswith=prefix
            ).order_by("-student_id").first()

            if last_student:
                last_number = int(
                    last_student.student_id.replace(prefix, "")
                )
                next_number = last_number + 1
            else:
                next_number = 10050

            self.student_id = f"{prefix}{next_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.student_name}"


# ==========================================================
# STUDENT CERTIFICATE
# ==========================================================

class StudentCertificate(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    certificate_title = models.CharField(max_length=200)
    certificate_number = models.CharField(max_length=100, blank=True)

    issue_date = models.DateField(
        null=True,
        blank=True
    )

    certificate_file = models.FileField(
        upload_to='students/certificates/'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.student.student_name} - "
            f"{self.certificate_title}"
        )


# ==========================================================
# FCM DEVICE
# ==========================================================

class FCMDevice(models.Model):

    DEVICE_CHOICES = [
        ("ANDROID", "Android"),
        ("IOS", "iOS"),
        ("WEB", "Web"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fcm_devices"
    )

    device = models.CharField(
        max_length=10,
        choices=DEVICE_CHOICES
    )

    device_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    reg_token = models.TextField(unique=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fcm_device"

    def __str__(self):
        return f"{self.user.email} - {self.device}"


# ==========================================================
# STUDENT LESSON PROGRESS
# ==========================================================

class StudentLessonProgress(models.Model):

    student = models.ForeignKey(
        "Student",
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )

    lesson = models.ForeignKey(
        "courses.Lesson",
        on_delete=models.CASCADE,
        related_name="student_progress"
    )

    is_completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_satisfied = models.BooleanField(default=False)
    student_review = models.TextField(blank=True)

    class Meta:
        unique_together = ["student", "lesson"]
        ordering = ["lesson__lesson_order"]

    def save(self, *args, **kwargs):

        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()

        elif not self.is_completed:
            self.completed_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.student_name} - {self.lesson.lesson_title}"


# ==========================================================
# STAFF MODEL
# ==========================================================

class Staff(models.Model):

    DOMAIN_CHOICES = [
        ("PYTHON", "Python Full Stack"),
        ("FLUTTER", "Flutter Development"),
        ("MERN", "MERN Stack"),
        ("JAVA", "Java Full Stack"),
        ("UIUX", "UI/UX Design"),
        ("DIGITAL_MARKETING", "Digital Marketing"),
        ("DATA_ANALYTICS", "Data Analytics"),
        ("TESTING", "Software Testing"),
        ("DEVOPS", "DevOps"),
        ("OTHER", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="staff_profile"
    )

    staff_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    staff_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="staffs"
    )

    domain = models.CharField(
        max_length=30,
        choices=DOMAIN_CHOICES
    )

    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.staff_id:

            last_staff = Staff.objects.order_by("-id").first()

            if last_staff:
                last_number = int(
                    last_staff.staff_id.replace("STF", "")
                )
                self.staff_id = f"STF{last_number + 1:04d}"

            else:
                self.staff_id = "STF0001"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff_name} ({self.staff_id})"


# ==========================================================
# PAYMENT TYPE MODEL
# ==========================================================

class PaymentType(models.Model):

    payment_type_name = models.CharField(
        max_length=100,
        unique=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.payment_type_name
