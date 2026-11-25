from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from students.permissions import UserPermission
from .models import InternshipStudent, Vacancy
from .serializers import InternshipStudentSerializer, VacancySerializer


class InternshipStudentAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_internshipstudent",
        "POST": "add_internshipstudent",
        "PUT": "change_internshipstudent",
        "PATCH": "change_internshipstudent",
        "DELETE": "delete_internshipstudent",
    }

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):

        if pk:
            student = get_object_or_404(
                InternshipStudent,
                pk=pk,
            )

            serializer = InternshipStudentSerializer(student)

            return Response(serializer.data)

        queryset = InternshipStudent.objects.all().order_by("-created_at")

        serializer = InternshipStudentSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = InternshipStudentSerializer(
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
            InternshipStudent,
            pk=pk,
        )

        serializer = InternshipStudentSerializer(
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
            InternshipStudent,
            pk=pk,
        )

        student.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )



class VacancyAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_vacancy",
        "POST": "add_vacancy",
        "PUT": "change_vacancy",
        "PATCH": "change_vacancy",
        "DELETE": "delete_vacancy",
    }

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):
        # Single vacancy
        if pk:
            vacancy = get_object_or_404(Vacancy, pk=pk)
            serializer = VacancySerializer(vacancy)
            return Response(serializer.data)
        queryset = Vacancy.objects.all()

        # Filters
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true"
            )

        department = request.query_params.get("department")
        if department:
            queryset = queryset.filter(
                department__icontains=department
            )

        job_type = request.query_params.get("job_type")
        if job_type:
            queryset = queryset.filter(job_type=job_type)

        location = request.query_params.get("location")
        if location:
            queryset = queryset.filter(
                location__icontains=location
            )

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(department__icontains=search) |
                Q(location__icontains=search)
            )

        ordering = request.query_params.get("ordering")

        allowed = [
            "display_order",
            "-display_order",
            "created_at",
            "-created_at",
            "title",
            "-title",
        ]

        if ordering in allowed:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("display_order")

        serializer = VacancySerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = VacancySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def put(self, request, pk):
        vacancy = get_object_or_404(Vacancy, pk=pk)
        serializer = VacancySerializer(
            vacancy,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        vacancy = get_object_or_404(Vacancy, pk=pk)
        serializer = VacancySerializer(
            vacancy,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):

        vacancy = get_object_or_404(Vacancy, pk=pk)
        vacancy.delete()
        return Response(
            {"message": "Vacancy deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )