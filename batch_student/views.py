from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BatchStudent
from .serializers import BatchStudentSerializer


class BatchStudentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            batch_student = get_object_or_404(
                BatchStudent.objects.select_related("batch", "student"),
                pk=pk
            )
            serializer = BatchStudentSerializer(batch_student)
            return Response(serializer.data)

        queryset = BatchStudent.objects.select_related("batch", "student").order_by("roll_number")
        batch = request.query_params.get("batch")
        if batch:
            queryset = queryset.filter(batch=batch)
        status_param = request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        serializer = BatchStudentSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BatchStudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        batch_student = get_object_or_404(BatchStudent, pk=pk)
        serializer = BatchStudentSerializer(batch_student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        batch_student = get_object_or_404(BatchStudent, pk=pk)
        batch_student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)