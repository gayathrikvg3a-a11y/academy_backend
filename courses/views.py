from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.pagination import get_paginator_class
from students.permissions import UserPermission

from .models import AcademicInternship, Blog, CaseStudy, ContactInformation, Course, CourseCategory, CourseFeeOption, CurriculumModule, CurriculumTopic, IndustryInternship, Lesson, LifeAtCignes
from .serializers import (
    AcademicInternshipSerializer,
    BlogSerializer,
    CaseStudySerializer,
    ContactInformationSerializer,
    CourseCategorySerializer,
    CourseFeeOptionSerializer,
    CourseSerializer,
    CurriculumModuleSerializer,
    CurriculumTopicSerializer,
    IndustryInternshipSerializer,
    LessonSerializer,
    LifeAtCignesSerializer,
)


class CourseAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_course",
        "POST": "add_course",
        "PUT": "change_course",
        "PATCH": "change_course",
        "DELETE": "delete_course",
    }

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):

        queryset = Course.objects.select_related("category").prefetch_related(
            "students",
            "fee_options",
            "curriculum_modules__topics__lessons",   # Topics with Lessons
        )

        # Get single course
        if pk:
            course = get_object_or_404(queryset, pk=pk)
            serializer = CourseSerializer(
                course,
                context={"request": request}
            )
            return Response(serializer.data)

        # Course list
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true"
            )

        serializer = CourseSerializer(
            queryset,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(
            course,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurriculumModuleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            module = get_object_or_404(CurriculumModule, pk=pk)
            serializer = CurriculumModuleSerializer(module)
            return Response(serializer.data)

        queryset = CurriculumModule.objects.all().order_by("module_order")
        course_id = request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        serializer = CurriculumModuleSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CurriculumModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)

        serializer = CourseSerializer(
            course,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        module = get_object_or_404(CurriculumModule, pk=pk)
        serializer = CurriculumModuleSerializer(module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        module = get_object_or_404(CurriculumModule, pk=pk)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurriculumTopicAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            topic = get_object_or_404(
                CurriculumTopic.objects.select_related("module", "module__course"),
                pk=pk
            )
            serializer = CurriculumTopicSerializer(topic)
            return Response(serializer.data)

        queryset = CurriculumTopic.objects.select_related("module", "module__course").all()
        module_id = request.query_params.get("module")
        if module_id:
            queryset = queryset.filter(module_id=module_id)

        serializer = CurriculumTopicSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CurriculumTopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        topic = get_object_or_404(CurriculumTopic, pk=pk)
        serializer = CurriculumTopicSerializer(topic, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        topic = get_object_or_404(CurriculumTopic, pk=pk)
        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LessonAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            lesson = get_object_or_404(
                Lesson.objects.select_related("course", "module"),
                pk=pk
            )
            serializer = LessonSerializer(lesson)
            return Response(serializer.data)

        queryset = Lesson.objects.select_related("course", "module").order_by("lesson_order")
        course_id = request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        module_id = request.query_params.get("module")
        if module_id:
            queryset = queryset.filter(module_id=module_id)

        serializer = LessonSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        lesson = get_object_or_404(Lesson, pk=pk)
        serializer = LessonSerializer(lesson, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        lesson = get_object_or_404(Lesson, pk=pk)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseFeeOptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id=None, pk=None):

        # Get single fee option
        if pk:
            fee_option = get_object_or_404(CourseFeeOption, pk=pk)
            serializer = CourseFeeOptionSerializer(fee_option)
            return Response(serializer.data)

        # List fee options
        queryset = CourseFeeOption.objects.filter(
            is_active=True
        ).select_related("course").order_by("id")

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        # Use your pagination utility
        paginator_class = get_paginator_class(request)
        paginator = paginator_class()

        page = paginator.paginate_queryset(queryset, request)

        serializer = CourseFeeOptionSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, course_id=None):
        course = get_object_or_404(Course, pk=course_id)

        serializer = CourseFeeOptionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, course_id=None, pk=None):
        fee_option = get_object_or_404(CourseFeeOption, pk=pk)

        serializer = CourseFeeOptionSerializer(
            fee_option,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id=None, pk=None):
        fee_option = get_object_or_404(CourseFeeOption, pk=pk)
        fee_option.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseListAPIView(APIView):
    permission_classes = []

    def get(self, request, pk=None):

        if pk:
            course = Course.objects.prefetch_related(
                "curriculum_modules__topics",
                "curriculum_modules__lessons",
                "fee_options",
            ).filter(pk=pk, is_active=True).first()

            if not course:
                return Response(
                    {"message": "Course not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            data = {
                "id": course.id,
                "name": course.name,
                "course_code": course.course_code,
                "details": course.details,
                "duration": course.duration,
                "duration_type": course.duration_type,
                "level": course.level,
                "thumbnail": request.build_absolute_uri(course.thumbnail.url)
                    if course.thumbnail else None,

                "title": course.title,
                "mode": course.mode,
                "slug": course.slug,
                "short_description": course.short_description,
                "seo_title": course.seo_title,
                "seo_description": course.seo_description,
                "seo_keywords": course.seo_keywords,
                "canonical_url": course.canonical_url,
                "og_image": request.build_absolute_uri(course.og_image.url)
                    if course.og_image else None,

                "fee_options": [
                    {
                        "id": fee.id,
                        "option_name": fee.option_name,
                        "fee": fee.fee,
                    }
                    for fee in course.fee_options.filter(is_active=True)
                ],

                "curriculum_modules": [
                    {
                        "id": module.id,
                        "title": module.title,
                        "description": module.description,
                        "module_order": module.module_order,

                        "topics": [
                            {
                                "id": topic.id,
                                "title": topic.title,
                                "description": topic.description,
                                "topic_order": topic.topic_order,
                            }
                            for topic in module.topics.all()
                        ],

                        "lessons": [
                            {
                                "id": lesson.id,
                                "lesson_title": lesson.lesson_title,
                                "description": lesson.description,
                                "lesson_order": lesson.lesson_order,
                                "duration_minutes": lesson.duration_minutes,
                                "video_url": lesson.video_url,
                                "notes": lesson.notes,
                                "pdf_file": request.build_absolute_uri(lesson.pdf_file.url)
                                    if lesson.pdf_file else None,
                            }
                            for lesson in module.lessons.filter(is_published=True)
                        ],
                    }
                    for module in course.curriculum_modules.all()
                ],
            }

            return Response(data)

        courses = Course.objects.filter(is_active=True)

        data = [
            {
                "id": course.id,
                "name": course.name,
                "title": course.title,
                "slug": course.slug,
                "short_description": course.short_description,
                "seo_title": course.seo_title,
                "seo_description": course.seo_description,
                "seo_keywords": course.seo_keywords,
                "canonical_url": course.canonical_url,
                "og_image": request.build_absolute_uri(course.og_image.url)
                    if course.og_image else None,

                "course_code": course.course_code,
                "details": course.details,
                "duration": course.duration,
                "duration_type": course.duration_type,
                "level": course.level,
                "mode": course.mode,
                "thumbnail": request.build_absolute_uri(course.thumbnail.url)
                    if course.thumbnail else None,
            }
            for course in courses
        ]

        return Response(data, status=status.HTTP_200_OK)


class BlogAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk=None):
        if pk:
            blog = get_object_or_404(Blog, pk=pk, is_active=True)
            serializer = BlogSerializer(blog, context={"request": request})
            return Response(serializer.data)

        blogs = Blog.objects.filter(is_active=True)
        serializer = BlogSerializer(
            blogs,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = BlogSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        blog = get_object_or_404(Blog, pk=pk)
        serializer = BlogSerializer(
            blog,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        blog = get_object_or_404(Blog, pk=pk)

        blog.is_active = False
        blog.save(update_fields=["is_active"])

        return Response(
            {
                "status": True,
                "message": "Blog deleted successfully."
            },
            status=status.HTTP_200_OK,
        )


class CourseCategoryAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]          
        return [IsAuthenticated()]

    def get(self, request, pk=None):
        if pk:
            category = get_object_or_404(
                CourseCategory.objects.prefetch_related("courses"),
                pk=pk
            )

            # Courses displayed according to display_order
            courses = category.courses.filter(
                is_active=True
            ).order_by("display_order", "name")

            return Response({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "display_order": category.display_order,
                "is_active": category.is_active,
                "created_at": category.created_at,

                "courses": [
                    {
                        "id": course.id,
                        "name": course.name,
                        "course_code": course.course_code,
                        "duration": course.duration,
                        "duration_type": course.duration_type,
                        "language": course.language,
                        "level": course.level,
                        "course_fee": course.course_fee,
                        "discount_fee": course.discount_fee,
                        "final_fee": (
                            course.discount_fee
                            if course.discount_fee
                            else course.course_fee
                        ),
                        "thumbnail_url": (
                            request.build_absolute_uri(course.thumbnail.url)
                            if course.thumbnail
                            else None
                        ),
                    }
                    for course in courses
                ]
            })

        # GET All Categories - ordered by display_order
        categories = CourseCategory.objects.order_by(
            "display_order",
            "name"
        )

        return Response([
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "display_order": category.display_order,
                "is_active": category.is_active,
                "created_at": category.created_at,
            }
            for category in categories
        ])

    def post(self, request):
        serializer = CourseCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        category = get_object_or_404(CourseCategory, pk=pk)
        serializer = CourseCategorySerializer(category, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(CourseCategory, pk=pk)
        category.delete()

        return Response(
            {
                "status": True,
                "message": "Course category deleted successfully."
            },
            status=status.HTTP_200_OK
        )


class LifeAtCignesAPIView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        images = LifeAtCignes.objects.all()

        serializer = LifeAtCignesSerializer(
            images,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = LifeAtCignesSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        image = get_object_or_404(
            LifeAtCignes,
            pk=pk
        )

        serializer = LifeAtCignesSerializer(
            image,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk=None):
        image = get_object_or_404(
            LifeAtCignes,
            pk=pk
        )

        image.delete()

        return Response(
            {
                "message": "Image deleted successfully."
            },
            status=status.HTTP_200_OK
        )

class SelectedLifeAtCignesAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        images = LifeAtCignes.objects.filter(
            is_selected=True
        )
        serializer = LifeAtCignesSerializer(
            images,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)


class SelectLifeAtCignesAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_ids = request.data.get("image_ids", [])

        if not isinstance(image_ids, list):
            return Response(
                {"message": "image_ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(image_ids) < 1 or len(image_ids) > 5:
            return Response(
                {"message": "You can select between 1 and 5 images."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(set(image_ids)) != len(image_ids):
            return Response(
                {"message": "Duplicate image IDs are not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        images = LifeAtCignes.objects.filter(
            id__in=image_ids
        )

        if images.count() != len(image_ids):
            return Response(
                {"message": "Some image IDs are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # First unselect all images
        LifeAtCignes.objects.update(
            is_selected=False
        )

        # Then select submitted images
        images.update(
            is_selected=True
        )

        serializer = LifeAtCignesSerializer(
            images,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "message": f"{len(image_ids)} image(s) selected successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class ContactInformationAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk=None):
        if pk:
            contact = get_object_or_404(
                ContactInformation,
                pk=pk
            )
            serializer = ContactInformationSerializer(contact)
            return Response(serializer.data)

        contacts = ContactInformation.objects.all()
        serializer = ContactInformationSerializer(
            contacts,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactInformationSerializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):

        contact = get_object_or_404(
            ContactInformation,
            pk=pk
        )
        serializer = ContactInformationSerializer(
            contact,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk=None):

        contact = get_object_or_404(
            ContactInformation,
            pk=pk
        )
        contact.delete()
        return Response(
            {
                "message": "Contact information deleted successfully."
            },
            status=status.HTTP_200_OK
        )


class AcademicInternshipAPIView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        internships = AcademicInternship.objects.all()

        serializer = AcademicInternshipSerializer(
            internships,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = AcademicInternshipSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        internship = get_object_or_404(
            AcademicInternship,
            pk=pk
        )

        serializer = AcademicInternshipSerializer(
            internship,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk=None):
        internship = get_object_or_404(
            AcademicInternship,
            pk=pk
        )
        internship.delete()
        return Response(
            {"message": "Academic internship deleted successfully."},
            status=status.HTTP_200_OK
        )


class SelectAcademicInternshipAPIView(APIView):

    permission_classes = [IsAuthenticated]
    def post(self, request):
        internship_ids = request.data.get("internship_ids", [])
        if not isinstance(internship_ids, list):
            return Response(
                {"message": "internship_ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(internship_ids) < 1 or len(internship_ids) > 4:
            return Response(
                {"message": "You can select between 1 and 4 internships."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(set(internship_ids)) != len(internship_ids):
            return Response(
                {"message": "Duplicate internship IDs are not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        internships = AcademicInternship.objects.filter(
            id__in=internship_ids
        )

        if internships.count() != len(internship_ids):
            return Response(
                {"message": "Some internship IDs are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        AcademicInternship.objects.update(
            is_selected=False
        )

        internships.update(
            is_selected=True
        )

        serializer = AcademicInternshipSerializer(
            internships,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "message": f"{len(internship_ids)} internship(s) selected successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class SelectedAcademicInternshipAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        internships = AcademicInternship.objects.filter(
            is_selected=True
        )
        serializer = AcademicInternshipSerializer(
            internships,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)


class IndustryInternshipAPIView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        internships = IndustryInternship.objects.all()

        serializer = IndustryInternshipSerializer(
            internships,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = IndustryInternshipSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        internship = get_object_or_404(
            IndustryInternship,
            pk=pk
        )

        serializer = IndustryInternshipSerializer(
            internship,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk=None):
        internship = get_object_or_404(
            IndustryInternship,
            pk=pk
        )

        internship.delete()

        return Response(
            {"message": "Industry internship deleted successfully."},
            status=status.HTTP_200_OK
        )


class SelectIndustryInternshipAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        internship_ids = request.data.get("internship_ids", [])

        if not isinstance(internship_ids, list):
            return Response(
                {"message": "internship_ids must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(internship_ids) < 1 or len(internship_ids) > 5:
            return Response(
                {"message": "You can select between 1 and 5 internships."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(set(internship_ids)) != len(internship_ids):
            return Response(
                {"message": "Duplicate internship IDs are not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        internships = IndustryInternship.objects.filter(
            id__in=internship_ids
        )

        if internships.count() != len(internship_ids):
            return Response(
                {"message": "Some internship IDs are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Unselect all
        IndustryInternship.objects.update(
            is_selected=False
        )

        # Select submitted internships
        internships.update(
            is_selected=True
        )

        serializer = IndustryInternshipSerializer(
            internships,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "message": f"{len(internship_ids)} internship(s) selected successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class SelectedIndustryInternshipAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        internships = IndustryInternship.objects.filter(
            is_selected=True
        )

        serializer = IndustryInternshipSerializer(
            internships,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


class CaseStudyAPIView(APIView):

    parser_classes = (
        MultiPartParser,
        FormParser,
        JSONParser
    )

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk=None):

        if pk:
            case_study = get_object_or_404(
                CaseStudy,
                pk=pk
            )
            serializer = CaseStudySerializer(
                case_study,
                context={"request": request}
            )
            return Response(serializer.data)

        case_studies = CaseStudy.objects.filter(
            is_active=True
        )
        serializer = CaseStudySerializer(
            case_studies,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):

        serializer = CaseStudySerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):

        case_study = get_object_or_404(
            CaseStudy,
            pk=pk
        )
        serializer = CaseStudySerializer(
            case_study,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk=None):

        case_study = get_object_or_404(
            CaseStudy,
            pk=pk
        )
        case_study.is_active = False
        case_study.save()
        return Response(
            {
                "message": "Case study deleted successfully."
            },
            status=status.HTTP_200_OK
        )