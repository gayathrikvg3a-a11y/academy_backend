from django.urls import path

from .views import (
    EnquiryAPIView,
    EnquiryConvertToStudentAPIView,
    CallHistoryAPIView,
    EnquiryNewAPIView,
    TestimonialAPIView,
)

urlpatterns = [
    path("enquiries/", EnquiryAPIView.as_view(), name="enquiry-list-create"),
    path("enquiries/<int:pk>/", EnquiryAPIView.as_view(), name="enquiry-detail"),
    path("enquiries/<int:pk>/convert-to-student/", EnquiryConvertToStudentAPIView.as_view(), name="enquiry-convert-to-student"),
    path("call-history/", CallHistoryAPIView.as_view(), name="call-history-list-create"),
    path("call-history/<int:pk>/", CallHistoryAPIView.as_view(), name="call-history-detail"),

    path("enquiry-new/", EnquiryNewAPIView.as_view(), name="enquiry-new-list-create"),
    path("enquiry-new/<int:pk>/", EnquiryNewAPIView.as_view(), name="enquiry-new-detail"),

    path("testimonials/", TestimonialAPIView.as_view()),
    path("testimonials/<int:pk>/", TestimonialAPIView.as_view()),
]