from django.urls import path

from .views import (
    BatchAPIView,
    BatchStudentsAPIView,
    BatchAssignStudentAPIView,
    BatchRemoveStudentAPIView,
    BatchAvailableStudentsAPIView,
)

urlpatterns = [
    path("batches/", BatchAPIView.as_view(), name="batch-list-create"),
    path("batches/<int:pk>/", BatchAPIView.as_view(), name="batch-detail"),
    path("batches/<int:pk>/students/", BatchStudentsAPIView.as_view(), name="batch-students"),
    path("batches/<int:pk>/assign_student/", BatchAssignStudentAPIView.as_view(), name="batch-assign-student"),
    path("batches/<int:pk>/remove_student/", BatchRemoveStudentAPIView.as_view(), name="batch-remove-student"),
    path("batches/<int:pk>/available_students/", BatchAvailableStudentsAPIView.as_view(), name="batch-available-students"),
]
 