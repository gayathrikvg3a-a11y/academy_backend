from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from events.pagination import CustomPagination, get_paginator_class
from students.permissions import UserPermission

from .models import Enquiry, CallHistory, EnquiryNew, Testimonial
from .serializers import EnquiryNewSerializer, EnquirySerializer, CallHistorySerializer, TestimonialSerializer

from students.models import Student
from students.serializers import StudentSerializer


class EnquiryAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_enquiry",
        "POST": "add_enquiry",
        "PUT": "change_enquiry",
        "PATCH": "change_enquirystatus",
        "DELETE": "delete_enquiry",
    }

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)
    
    def get(self, request, pk=None):
        if pk:
            enquiry = get_object_or_404(Enquiry, pk=pk)
            serializer = EnquirySerializer(enquiry)
            return Response(serializer.data)

        queryset = Enquiry.objects.all().order_by("-created_at")
        serializer = EnquirySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EnquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        enquiry = get_object_or_404(Enquiry, pk=pk)
        serializer = EnquirySerializer(enquiry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        enquiry = get_object_or_404(Enquiry, pk=pk)
        enquiry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnquiryConvertToStudentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk=None):
        enquiry = get_object_or_404(Enquiry, pk=pk)

        if enquiry.is_converted:
            return Response(
                {'error': 'This enquiry is already converted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not enquiry.course:
            return Response(
                {'error': 'Course is required before conversion.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        student = Student.objects.create(
            student_name=enquiry.student_name,
            phone=enquiry.phone,
            college=enquiry.college,
            academic_stream=enquiry.academic_stream,
            course=enquiry.course,
            course_fee=enquiry.course.course_fee,
            recommended_by=enquiry.recommended_by,
            enquiry=enquiry
        )

        enquiry.is_converted = True
        enquiry.enquiry_stage = 'CONVERTED'
        enquiry.save(update_fields=['is_converted', 'enquiry_stage', 'updated_at'])

        return Response(
            {
                'message': 'Enquiry converted to student successfully.',
                'student': StudentSerializer(student).data
            },
            status=status.HTTP_201_CREATED
        )


class CallHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            call_history = get_object_or_404(CallHistory, pk=pk)
            serializer = CallHistorySerializer(call_history)
            return Response(serializer.data)

        queryset = CallHistory.objects.all().order_by("-created_at")
        enquiry_id = request.query_params.get("enquiry")
        if enquiry_id:
            queryset = queryset.filter(enquiry_id=enquiry_id)

        serializer = CallHistorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CallHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        call_history = get_object_or_404(CallHistory, pk=pk)
        serializer = CallHistorySerializer(call_history, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        call_history = get_object_or_404(CallHistory, pk=pk)
        call_history.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnquiryNewAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]          
        return [IsAuthenticated()]      

    def post(self, request):
        serializer = EnquiryNewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Enquiry submitted successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "status": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, pk=None):
        if pk:
            enquiry = get_object_or_404(EnquiryNew, pk=pk)
            serializer = EnquiryNewSerializer(enquiry)
            return Response(
                {
                    "status": True,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        enquiries = EnquiryNew.objects.all()

        paginator_class = get_paginator_class(request)
        paginator = paginator_class()

        page = paginator.paginate_queryset(enquiries, request)

        if page is not None:
            serializer = EnquiryNewSerializer(page, many=True)
            response = paginator.get_paginated_response(serializer.data)
            response.data["status"] = True
            return response

        serializer = EnquiryNewSerializer(enquiries, many=True)
        return Response(
            {
                "status": True,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        enquiry = get_object_or_404(EnquiryNew, pk=pk)

        serializer = EnquiryNewSerializer(
            enquiry,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Enquiry updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        enquiry = get_object_or_404(EnquiryNew, pk=pk)
        status_value = request.data.get("status")

        if not status_value:
            return Response(
                {
                    "status": False,
                    "message": "Status is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        enquiry.status = status_value
        enquiry.save(update_fields=["status"])

        return Response(
            {
                "status": True,
                "message": "Enquiry status updated successfully.",
                "data": {
                    "id": enquiry.id,
                    "status": enquiry.status,
                },
            },
            status=status.HTTP_200_OK,
        )


class TestimonialAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]          # Public GET
        return [IsAuthenticated()]    # Other APIs require login

    def get(self, request, pk=None):
        if pk:
            testimonial = get_object_or_404(
                Testimonial,
                pk=pk,
                is_active=True
            )
            serializer = TestimonialSerializer(testimonial)
            return Response(serializer.data)

        queryset = Testimonial.objects.filter(is_active=True)

        domain = request.query_params.get("domain")
        if domain:
            queryset = queryset.filter(domain__icontains=domain)

        serializer = TestimonialSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TestimonialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        testimonial = get_object_or_404(Testimonial, pk=pk)
        serializer = TestimonialSerializer(
            testimonial,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        testimonial = get_object_or_404(Testimonial, pk=pk)
        testimonial.is_active = False
        testimonial.save(update_fields=["is_active"])
        return Response(
            {"message": "Testimonial deleted successfully."},
            status=status.HTTP_200_OK
        )