from django.urls import path
from .views import (ChangePasswordAPIView,LogoutFCMDeviceAPIView, StaffAPIView,StudentAPIView,StudentCertificateAPIView, StudentLessonChecklistAPIView, StudentMyChecklistAPIView,StudentProfileAPIView, StudentProgressAPIView,UpdateFCMTokenAPIView,)
from .views import PaymentTypeAPIView
urlpatterns = [
    path("students/",StudentAPIView.as_view(),),
    path("students/<int:pk>/",StudentAPIView.as_view(),),
    path("student-certificates/",StudentCertificateAPIView.as_view(),),
    path("student-certificates/<int:pk>/",StudentCertificateAPIView.as_view(),),
    path("student-profile/",StudentProfileAPIView.as_view(),name="student-profile",),
    path("fcm-token/",UpdateFCMTokenAPIView.as_view(),name="update-fcm-token",),
    path("logout-fcm-device/",LogoutFCMDeviceAPIView.as_view(),name="logout-fcm-device",),
    path("change-password/",ChangePasswordAPIView.as_view(),name="change-password",),

    path("students/<int:student_id>/checklist/",StudentLessonChecklistAPIView.as_view(),name="student-checklist"),
    path("students/<int:student_id>/progress/",StudentProgressAPIView.as_view(),name="student-progress"),

    path("student-my-checklist/",StudentMyChecklistAPIView.as_view(),name="student-my-checklist",),

    path("staffs/", StaffAPIView.as_view()),
    path("staffs/<int:pk>/", StaffAPIView.as_view()),
    path('payment-types/',PaymentTypeAPIView.as_view(),name='payment-types'),
    path('payment-types/<int:pk>/',PaymentTypeAPIView.as_view(),name='payment-type-detail'),

]