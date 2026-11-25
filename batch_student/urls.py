from django.urls import path

from .views import BatchStudentAPIView

urlpatterns = [
    path("batch-students/", BatchStudentAPIView.as_view(), name="batch-student-list-create"),
    path("batch-students/<int:pk>/", BatchStudentAPIView.as_view(), name="batch-student-detail"),
]
