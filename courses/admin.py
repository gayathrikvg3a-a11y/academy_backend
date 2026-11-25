from django.contrib import admin
from .models import AcademicInternship, CaseStudy, ContactInformation, Course, CourseCategory, CurriculumModule, CurriculumTopic, IndustryInternship, Lesson, LifeAtCignes


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'duration',
        'course_fee',
        'is_active',
        'created_at',
    )

    list_filter = ('is_active',)

    search_fields = ('name',)

admin.site.register(Lesson)
admin.site.register(CurriculumModule)
admin.site.register(CurriculumTopic)
admin.site.register(CourseCategory)
admin.site.register(LifeAtCignes)
admin.site.register(ContactInformation)
admin.site.register(AcademicInternship)
admin.site.register(IndustryInternship)
admin.site.register(CaseStudy)