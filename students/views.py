from django.db.models import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from courses.models import Lesson
from students.permissions import UserPermission
from .models import (FCMDevice, Staff, Student,StudentCertificate, StudentLessonProgress,)
from .serializers import (FCMDeviceSerializer, LogoutFCMDeviceSerializer, StaffSerializer, StudentProfileSerializer, StudentProfileUpdateSerializer, StudentSerializer,StudentCertificateSerializer,)
from .pagination import StudentPagination
from rest_framework import status, permissions
from django.contrib.auth.models import User
from .models import PaymentType



class StudentAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_student",
        "POST": "add_student",
        "PUT": "change_student",
        "PATCH": "change_student",
        "DELETE": "delete_student",
    }

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):

        if pk:

            student = get_object_or_404(
                Student.objects.select_related(
                    "course",
                    "fee_type",
                    "batch",
                    "enquiry",
                ),
                pk=pk,
            )

            serializer = StudentSerializer(student)

            return Response(serializer.data)

        queryset = Student.objects.select_related(
            "course",
            "fee_type",
            "batch",
            "enquiry",
        ).all().order_by("-created_at")

        # Filters

        course = request.query_params.get("course")
        if course:
            queryset = queryset.filter(course=course)

        fee_type = request.query_params.get("fee_type")
        if fee_type:
            queryset = queryset.filter(fee_type=fee_type)

        batch = request.query_params.get("batch")
        if batch:
            queryset = queryset.filter(batch=batch)

        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Search

        search = request.query_params.get("search")

        if search:

            queryset = queryset.filter(
                student_id__icontains=search
            ) | queryset.filter(
                student_name__icontains=search
            ) | queryset.filter(
                phone__icontains=search
            )

        # Ordering

        ordering = request.query_params.get("ordering")

        allowed = [
            "student_name",
            "-student_name",
            "joining_date",
            "-joining_date",
            "course_fee",
            "-course_fee",
            "created_at",
            "-created_at",
        ]

        if ordering in allowed:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-created_at")

        # Pagination

        paginator = StudentPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
        )

        serializer = StudentSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data,
        )

    def post(self, request):

        serializer = StudentSerializer(
            data=request.data,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):

        student = get_object_or_404(
            Student,
            pk=pk,
        )

        serializer = StudentSerializer(
            student,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk=None):
        student = get_object_or_404(
            Student,
            pk=pk,
            status="ACTIVE"
        )

        # Soft delete
        student.status = "DROPPED"
        student.save(update_fields=["status"])

        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================================
# STUDENT CERTIFICATE
# ==========================================================

class StudentCertificateAPIView(APIView):

    def get(self, request, pk=None):

        if pk:
            certificate = get_object_or_404(
                StudentCertificate.objects.select_related("student"),
                pk=pk,
            )

            serializer = StudentCertificateSerializer(certificate)
            return Response(serializer.data)

        queryset = StudentCertificate.objects.select_related(
            "student",
        ).all().order_by("-created_at")

        # Student login -> show only own certificates
        if hasattr(request.user, "student_profile"):
            queryset = queryset.filter(student=request.user.student_profile)

        # Admin/Staff login -> can filter by student ID
        else:
            student = request.query_params.get("student")

            if student:
                queryset = queryset.filter(student_id=student)

        serializer = StudentCertificateSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = StudentCertificateSerializer(
            data=request.data,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):

        certificate = get_object_or_404(
            StudentCertificate,
            pk=pk,
        )

        serializer = StudentCertificateSerializer(
            certificate,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk=None):

        certificate = get_object_or_404(
            StudentCertificate,
            pk=pk,
        )

        certificate.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )



class StudentProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = get_object_or_404(
            Student.objects.select_related(
                "course",
                "batch",
                "fee_type",
            ).prefetch_related(
                "payments",
                "payments__payment_type",
                "certificates",
                "course__curriculum_modules__topics",
                "course__curriculum_modules__lessons",
            ),
            user=request.user,
        )

        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)

    def patch(self, request):
        student = get_object_or_404(
            Student,
            user=request.user,
        )

        serializer = StudentProfileUpdateSerializer(
            student,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )




class UpdateFCMTokenAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FCMDeviceSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        device = serializer.validated_data["device"]
        device_id = serializer.validated_data["device_id"]
        reg_token = serializer.validated_data["reg_token"]

        FCMDevice.objects.update_or_create(
            user=request.user,
            device_id=device_id,
            defaults={
                "device": device,
                "reg_token": reg_token,
                "is_active": True,
            },
        )

        return Response(
            {
                "message": "FCM token updated successfully."
            },
            status=status.HTTP_200_OK,
        )



class LogoutFCMDeviceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutFCMDeviceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        device_id = serializer.validated_data["device_id"]
        device = FCMDevice.objects.filter(user=request.user,device_id=device_id).first()

        if device:
            device.is_active = False
            device.save(update_fields=["is_active"])

        return Response(
            {
                "message": "Device logged out successfully."
            },
            status=status.HTTP_200_OK,
        )



class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_id = request.data.get("user_id")
        password = request.data.get("password")
        if not user_id:
            return Response(
                {
                    "status": False,
                    "message": "User ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not password:
            return Response(
                {
                    "status": False,
                    "message": "Password is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except ObjectDoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            user.set_password(password)   # or make_password(password)
            user.save()

            return Response(
                {
                    "status": True,
                    "message": f"{user.username}'s password has been updated successfully."
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentLessonChecklistAPIView(APIView):

    def get(self, request, student_id):

        student = get_object_or_404(Student, pk=student_id)

        lessons = Lesson.objects.filter(
            course=student.course,
            is_published=True
        ).select_related("module")

        data = []

        for lesson in lessons:
            progress = StudentLessonProgress.objects.filter(
                student=student,
                lesson=lesson
            ).first()

            data.append({
                "lesson_id": lesson.id,
                "module": lesson.module.title,
                "lesson_title": lesson.lesson_title,
                "lesson_order": lesson.lesson_order,
                "is_completed": progress.is_completed if progress else False,
                "completed_at": progress.completed_at if progress else None,
            })

        return Response({
            "student_id": student.id,
            "student_name": student.student_name,
            "course": student.course.name if student.course else None,
            "lessons": data,
        })

    def post(self, request, student_id):

        student = get_object_or_404(Student, pk=student_id)

        lesson_id = request.data.get("lesson_id")
        is_completed = request.data.get("is_completed", True)
        remarks = request.data.get("remarks", "")

        lesson = get_object_or_404(Lesson, pk=lesson_id)

        progress, created = StudentLessonProgress.objects.get_or_create(
            student=student,
            lesson=lesson
        )

        progress.is_completed = is_completed
        progress.remarks = remarks
        progress.save()

        return Response({
            "message": "Checklist updated successfully",
            "is_completed": progress.is_completed,
        })


class StudentProgressAPIView(APIView):

    def get(self, request, student_id):

        student = get_object_or_404(Student, pk=student_id)

        total_lessons = Lesson.objects.filter(
            course=student.course,
            is_published=True
        ).count()

        completed_lessons = StudentLessonProgress.objects.filter(
            student=student,
            is_completed=True,
            lesson__course=student.course
        ).count()

        progress_percentage = 0
        if total_lessons > 0:
            progress_percentage = round(
                (completed_lessons / total_lessons) * 100
            )

        completed_ids = StudentLessonProgress.objects.filter(
            student=student,
            is_completed=True
        ).values_list("lesson_id", flat=True)

        next_lesson = Lesson.objects.filter(
            course=student.course,
            is_published=True
        ).exclude(
            id__in=completed_ids
        ).order_by(
            "module__module_order",
            "lesson_order"
        ).first()

        return Response({
            "student_id": student.id,
            "student_name": student.student_name,
            "course": student.course.name if student.course else None,
            "batch": student.batch.batch_name if student.batch else None,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percentage": progress_percentage,
            "next_lesson": next_lesson.lesson_title if next_lesson else None,
        })


class StudentMyChecklistAPIView(APIView):

    def get(self, request):
        # Logged-in student
        student = get_object_or_404(Student, user=request.user)
        lessons = Lesson.objects.filter(
            course=student.course,
            is_published=True
        ).select_related("module")

        data = []
        for lesson in lessons:
            progress = StudentLessonProgress.objects.filter(
                student=student,
                lesson=lesson
            ).first()
            data.append({
                "lesson_id": lesson.id,
                "module": lesson.module.title,
                "lesson_title": lesson.lesson_title,
                "lesson_order": lesson.lesson_order,
                "is_completed": progress.is_completed if progress else False,
                "completed_at": progress.completed_at if progress else None,
                "is_satisfied": progress.is_satisfied if progress else False,
                "student_review": progress.student_review if progress else "",
            })

        return Response({
            "student_id": student.id,
            "student_name": student.student_name,
            "course": student.course.name if student.course else None,
            "lessons": data,
        })

    def post(self, request):
        student = get_object_or_404(Student, user=request.user)
        lesson = get_object_or_404(Lesson,pk=request.data.get("lesson_id"))

        progress, created = StudentLessonProgress.objects.get_or_create(
            student=student,
            lesson=lesson
        )

        progress.is_satisfied = request.data.get("is_satisfied", False)
        progress.student_review = request.data.get("student_review", "")
        progress.save()

        return Response(
            {
                "status": True,
                "message": "Review submitted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class StaffAPIView(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):

        if pk:
            staff = get_object_or_404(
                Staff.objects.select_related("user"),
                pk=pk,
                is_active=True
            )

            serializer = StaffSerializer(staff)
            return Response(serializer.data)

        queryset = Staff.objects.select_related("user").filter(
            is_active=True
        ).order_by("-created_at")

        # Filters
        role = request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)

        domain = request.query_params.get("domain")
        if domain:
            queryset = queryset.filter(domain=domain)

        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true"
            )

        # Search
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(staff_name__icontains=search) |
                Q(staff_id__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )

        # Dropdown / All List
        data = request.query_params.get("data")
        if data == "alllist":
            return Response(
                queryset.values(
                    "id",
                    "staff_name",
                    "domain"
                )
            )

        # Pagination
        paginator = StudentPagination()      # or StaffPagination if you create one
        page = paginator.paginate_queryset(queryset, request)

        serializer = StaffSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


    def post(self, request):

        serializer = StaffSerializer(data=request.data)

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

        staff = get_object_or_404(Staff, pk=pk)

        serializer = StaffSerializer(
            staff,
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
        staff = get_object_or_404(
            Staff,
            pk=pk,
            is_active=True
        )

        staff.is_active = False
        staff.save(update_fields=["is_active"])

        return Response(
            {"message": "Staff deleted successfully."},
            status=status.HTTP_200_OK
        )
    # ==========================================================
# PAYMENT TYPE API
# ==========================================================


class PaymentTypeAPIView(APIView):

    permission_classes = [IsAuthenticated]

    # =========================================
    # GET - Display all active payment types
    # =========================================

    def get(self, request, pk=None):

        if pk:
            payment_type = get_object_or_404(
                PaymentType,
                pk=pk
            )

            data = {
                "id": payment_type.id,
                "payment_type_name": payment_type.payment_type_name,
                "is_active": payment_type.is_active,
            }

            return Response(
                data,
                status=status.HTTP_200_OK
            )

        payment_types = PaymentType.objects.filter(
            is_active=True
        ).order_by("payment_type_name")

        data = payment_types.values(
            "id",
            "payment_type_name",
            "is_active"
        )

        return Response(
            data,
            status=status.HTTP_200_OK
        )

    # =========================================
    # POST - Create new payment type
    # =========================================

    def post(self, request):

        payment_type_name = request.data.get(
            "payment_type_name"
        )

        if not payment_type_name or not payment_type_name.strip():

            return Response(
                {
                    "message": "Payment type name is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_type_name = payment_type_name.strip()

        if PaymentType.objects.filter(
            payment_type_name__iexact=payment_type_name
        ).exists():

            return Response(
                {
                    "message": "This payment type already exists."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_type = PaymentType.objects.create(
            payment_type_name=payment_type_name,
            is_active=request.data.get("is_active", True)
        )

        return Response(
            {
                "message": "Payment type created successfully.",
                "data": {
                    "id": payment_type.id,
                    "payment_type_name": payment_type.payment_type_name,
                    "is_active": payment_type.is_active,
                }
            },
            status=status.HTTP_201_CREATED
        )

    # =========================================
    # PUT - Complete update
    # =========================================

    def put(self, request, pk=None):

        if not pk:
            return Response(
                {
                    "message": "Payment type ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_type = get_object_or_404(
            PaymentType,
            pk=pk
        )

        payment_type_name = request.data.get(
            "payment_type_name"
        )

        if not payment_type_name or not payment_type_name.strip():

            return Response(
                {
                    "message": "Payment type name is required for PUT."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_type_name = payment_type_name.strip()

        if PaymentType.objects.filter(
            payment_type_name__iexact=payment_type_name
        ).exclude(pk=pk).exists():

            return Response(
                {
                    "message": "This payment type already exists."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_type.payment_type_name = payment_type_name
        payment_type.is_active = request.data.get(
            "is_active",
            payment_type.is_active
        )

        payment_type.save()

        return Response(
            {
                "message": "Payment type updated successfully.",
                "data": {
                    "id": payment_type.id,
                    "payment_type_name": payment_type.payment_type_name,
                    "is_active": payment_type.is_active,
                }
            },
            status=status.HTTP_200_OK
        )

    # =========================================
    # PATCH - Partial update
    # =========================================

    def patch(self, request, pk=None):

        if not pk:
            return Response(
                {
                    "message": "Payment type ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_type = get_object_or_404(
            PaymentType,
            pk=pk
        )

        payment_type_name = request.data.get(
            "payment_type_name"
        )

        if payment_type_name is not None:

            if not payment_type_name.strip():
                return Response(
                    {
                        "message": "Payment type name cannot be empty."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            payment_type_name = payment_type_name.strip()

            if PaymentType.objects.filter(
                payment_type_name__iexact=payment_type_name
            ).exclude(pk=pk).exists():

                return Response(
                    {
                        "message": "This payment type already exists."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            payment_type.payment_type_name = payment_type_name

        if "is_active" in request.data:
            payment_type.is_active = request.data["is_active"]

        payment_type.save()

        return Response(
            {
                "message": "Payment type updated successfully.",
                "data": {
                    "id": payment_type.id,
                    "payment_type_name": payment_type.payment_type_name,
                    "is_active": payment_type.is_active,
                }
            },
            status=status.HTTP_200_OK
        )

    # =========================================
    # DELETE - Soft delete
    # =========================================

    def delete(self, request, pk=None):

        if not pk:
            return Response(
                {
                    "message": "Payment type ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_type = get_object_or_404(
            PaymentType,
            pk=pk
        )

        payment_type.is_active = False
        payment_type.save(update_fields=["is_active", "updated_at"])

        return Response(
            {
                "message": "Payment type deactivated successfully."
            },
            status=status.HTTP_200_OK
        )
