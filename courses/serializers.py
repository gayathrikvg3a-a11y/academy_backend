from rest_framework import serializers


from .models import (
    AcademicInternship,
    Blog,
    CaseStudy,
    ContactInformation,
    Course,
    CourseCategory,
    CourseFeeOption,
    CurriculumModule,
    CurriculumTopic,
    IndustryInternship,
    Lesson,
    LifeAtCignes,
)



class LessonSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",          # ✅ Add
            "module",          # ✅ Add
            "topic", 
            "lesson_title",
            "description",
            "lesson_order",
            "duration_minutes",
            "video_url",
            "notes",
            "pdf_file",
            "pdf_url",
            "is_published",
        ]

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None



class CurriculumTopicSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = CurriculumTopic
        fields = [
            "id",
            "title",
            "module", 
            "description",
            "topic_order",
            "lessons",
        ]

class CurriculumModuleSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    topics = CurriculumTopicSerializer(many=True, read_only=True)

    class Meta:
        model = CurriculumModule
        fields = [
            "id",
            "course",          # ✅ Add this
            "title",
            "description",
            "module_order",
            "lesson_count",
            "topics",
        ]

    def get_lesson_count(self, obj):
        return obj.lessons.filter(is_published=True).count()


class CourseFeeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeeOption
        fields = [
            "id",
            "option_name",
            "fee",
            "is_active",
        ]


class CourseCategorySerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        model = CourseCategory
        fields = "__all__"

    def get_courses(self, obj):
        return CourseSerializer(
            obj.courses.filter(is_active=True),
            many=True,
            context=self.context
        ).data

         
class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    curriculum_modules = CurriculumModuleSerializer(
        many=True,
        read_only=True
    )

    fee_options = CourseFeeOptionSerializer(
        many=True,
        read_only=True
    )

    student_count = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    final_fee = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "course_code",
            "category",
            "category_name",
            "details",
            "duration",
            "duration_type",
            "duration_display",
            "language",
            "mode",
            "level",
            "level_display",
            "course_fee",
            "discount_fee",
            "final_fee",
            "thumbnail",
            "thumbnail_url",
            "title",
            "slug",
            "short_description",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "canonical_url",
            "og_image",
            "og_image_url",
            "learning_outcomes",
            "prerequisites",
            "certificate_available",
            "display_order",
            "student_count",
            "curriculum_modules",
            "fee_options",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        if "thumbnail" not in validated_data:
            validated_data["thumbnail"] = instance.thumbnail

        if "og_image" not in validated_data:
            validated_data["og_image"] = instance.og_image

        return super().update(instance, validated_data)

    def get_student_count(self, obj):
        return obj.students.count()

    def get_duration_display(self, obj):
        return f"{obj.duration} {obj.get_duration_type_display()}"

    def get_level_display(self, obj):
        return obj.get_level_display()

    def get_thumbnail_url(self, obj):
        if not obj.thumbnail:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.thumbnail.url)

        return obj.thumbnail.url

    def get_og_image_url(self, obj):
        if not obj.og_image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.og_image.url)

        return obj.og_image.url

    def get_final_fee(self, obj):
        return obj.discount_fee if obj.discount_fee else obj.course_fee

class StudentCourseSerializer(serializers.ModelSerializer):

    curriculum_modules = CurriculumModuleSerializer(
        many=True,
        read_only=True,
    )
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    duration_display = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    final_fee = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "course_code",
            "category",
            "category_name",
            "details",
            "duration",
            "duration_type",
            "duration_display",
            "language",
            "level",
            "level_display",
            "course_fee",
            "discount_fee",
            "final_fee",
            "thumbnail",
            "thumbnail_url",
            "learning_outcomes",
            "prerequisites",
            "certificate_available",
            "curriculum_modules",
        ]

    def get_duration_display(self, obj):
        return f"{obj.duration} {obj.get_duration_type_display()}"

    def get_level_display(self, obj):
        return obj.get_level_display()

    def get_thumbnail_url(self, obj):
        if not obj.thumbnail:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.thumbnail.url)

        return obj.thumbnail.url

    def get_final_fee(self, obj):
        return obj.discount_fee if obj.discount_fee else obj.course_fee


class BlogSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "canonical_url",
            "image",
            "image_url",
            "og_image",
            "og_image_url",
            "blog_date",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url

    def get_og_image_url(self, obj):
        if not obj.og_image:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.og_image.url)

        return obj.og_image.url


class LifeAtCignesSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = LifeAtCignes
        fields = [
            "id",
            "title",
            "image",
            "image_url",
            "is_selected",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ContactInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactInformation
        fields = [
            "id",
            "contact_number",
            "alternate_number",
            "whatsapp_number",
            "whatsapp_alternate",
            "email",
            "address",
            "maps",
            "created_at",
            "updated_at",
        ]


class AcademicInternshipSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AcademicInternship
        fields = [
            "id",
            "title",
            "image",
            "image_url",
            "is_selected",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url


class IndustryInternshipSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = IndustryInternship
        fields = [
            "id",
            "title",
            "image",
            "image_url",
            "is_selected",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url


class CaseStudySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CaseStudy
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "canonical_url",
            "image",
            "image_url",
            "og_image",
            "og_image_url",
            "case_study_date",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url

    def get_og_image_url(self, obj):
        if not obj.og_image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.og_image.url)

        return obj.og_image.url