from django.core.validators import FileExtensionValidator
from django.db import models

class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Course Category"
        verbose_name_plural = "Course Categories"

    def __str__(self):
        return self.name

class Course(models.Model):

    DURATION_TYPE_CHOICES = [
        ("DAYS", "Days"),
        ("WEEKS", "Weeks"),
        ("MONTHS", "Months"),
        ("YEARS", "Years"),
    ]

    LEVEL_CHOICES = [
        ("BEGINNER", "Beginner"),
        ("INTERMEDIATE", "Intermediate"),
        ("ADVANCED", "Advanced"),
    ]

    MODE_CHOICES = [
        ("ONLINE", "Online"),
        ("OFFLINE", "Offline"),
        ("ONLINE_OFFLINE", "Online / Offline"),
    ]

    name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=50,unique=True,null=True,blank=True)
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )
    mode = models.CharField(max_length=20,choices=MODE_CHOICES,default="ONLINE")

    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.CharField(max_length=500,blank=True,null=True)
    seo_title = models.CharField(max_length=255,blank=True,null=True)
    seo_description = models.TextField(blank=True,null=True)
    seo_keywords = models.TextField(blank=True,null=True)
    canonical_url = models.CharField(max_length=255, blank=True, null=True)
    og_image = models.ImageField(
        upload_to="courses/og-images/",
        blank=True,
        null=True
    )

    details = models.TextField(blank=True)
    duration = models.CharField(max_length=100,default="1")
    duration_type = models.CharField(max_length=20,choices=DURATION_TYPE_CHOICES,default="MONTHS")
    language = models.CharField(max_length=50,default="English")
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES,default="BEGINNER")
    course_fee = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    discount_fee = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    thumbnail = models.ImageField(upload_to="courses/thumbnails/",null=True,blank=True)
    learning_outcomes = models.JSONField(default=list,blank=True)
    prerequisites = models.JSONField(default=list,blank=True)
    certificate_available = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "display_order",
            "-created_at",
        ]

    def __str__(self):
        return self.name


class CurriculumModule(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="curriculum_modules"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    module_order = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "module_order",
            "id",
        ]

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class CurriculumTopic(models.Model):

    module = models.ForeignKey(
        CurriculumModule,
        on_delete=models.CASCADE,
        related_name="topics"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    topic_order = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "topic_order",
            "id",
        ]

    def __str__(self):
        return self.title


class Lesson(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    module = models.ForeignKey(
        CurriculumModule,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    topic = models.ForeignKey(
        CurriculumTopic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons"
    )

    lesson_title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    lesson_order = models.PositiveIntegerField(default=1)

    duration_minutes = models.PositiveIntegerField(default=0)

    video_url = models.CharField(max_length=500, blank=True)

    notes = models.TextField(blank=True)

    pdf_file = models.FileField(
        upload_to="courses/lessons/",
        blank=True,
        null=True
    )

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)


class CourseFeeOption(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="fee_options"
    )

    option_name = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "option_name")

    def __str__(self):
        return f"{self.course.name} - {self.option_name}"


class Blog(models.Model):
    title = models.CharField(max_length=255)
    
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    seo_keywords = models.TextField(null=True, blank=True)
    canonical_url = models.URLField(max_length=500, null=True, blank=True)
    og_image = models.ImageField(upload_to="blogs/og-images/",null=True,blank=True)

    short_description = models.CharField(max_length=500)
    description = models.TextField()
    image = models.ImageField(upload_to="blogs/", null=True, blank=True)
    blog_date = models.DateField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-blog_date", "-created_at"]

    def __str__(self):
        return self.title


class LifeAtCignes(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="life_at_cignes/")
    is_selected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ContactInformation(models.Model):
    contact_number = models.CharField(max_length=20)
    alternate_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    whatsapp_number = models.CharField(max_length=20)
    whatsapp_alternate = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    email = models.EmailField()
    address = models.TextField()
    maps = models.URLField(
        max_length=1000,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class AcademicInternship(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="academic_internships/")

    is_selected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class IndustryInternship(models.Model):
    title = models.CharField(max_length=255)

    image = models.ImageField(
        upload_to="industry_internships/"
    )

    is_selected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class CaseStudy(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True,null=True,blank=True)
    seo_title = models.CharField(max_length=255,null=True,blank=True)
    seo_description = models.TextField(null=True,blank=True)
    seo_keywords = models.TextField(null=True,blank=True)
    canonical_url = models.URLField(max_length=500,null=True,blank=True)
    og_image = models.ImageField(upload_to="case-studies/og-images/",null=True,blank=True)
    short_description = models.CharField(max_length=500)
    description = models.TextField()
    image = models.ImageField(
        upload_to="case-studies/",
        null=True,
        blank=True
    )

    case_study_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-case_study_date", "-created_at"]

    def __str__(self):
        return self.title