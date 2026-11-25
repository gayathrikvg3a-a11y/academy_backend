from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.pagination import get_paginator_class
from students.models import Student
from students.permissions import UserPermission
from students.serializers import StudentSerializer
from .models import Batch
from .serializers import BatchSerializer


class BatchAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_batch",
        "POST": "add_batch",
        "PUT": "change_batch",
        "PATCH": "change_batch",
        "DELETE": "delete_batch",
    }

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):
        if pk:
            batch = get_object_or_404(
                Batch.objects.select_related("course"),
                pk=pk
            )
            serializer = BatchSerializer(batch)
            return Response(serializer.data)

        queryset = Batch.objects.select_related("course").all()

        # Optional status filter
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        # Optional active filter
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Return all data without pagination
        if request.query_params.get("data") == "alllist":
            serializer = BatchSerializer(queryset, many=True)
            return Response(serializer.data)

        # Pagination
        paginator_class = get_paginator_class(request)
        paginator = paginator_class()

        page = paginator.paginate_queryset(queryset, request)

        serializer = BatchSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        batch = get_object_or_404(Batch, pk=pk)
        serializer = BatchSerializer(batch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        batch = get_object_or_404(Batch, pk=pk)
        batch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BatchStudentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        batch = get_object_or_404(Batch, pk=pk)
        students = Student.objects.filter(batch=batch)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


class BatchAssignStudentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        batch = get_object_or_404(Batch, pk=pk)
        student_id = request.data.get("student_id")
        try:
            student = Student.objects.get(id=student_id)
            student.batch = batch
            student.save()
            return Response({"message": "Student assigned successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BatchRemoveStudentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        student_id = request.data.get("student_id")
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        student.batch = None
        student.save()
        return Response({"message": "Student removed successfully"})


class BatchAvailableStudentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        batch = get_object_or_404(Batch, pk=pk)
        students = Student.objects.filter(course=batch.course)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)