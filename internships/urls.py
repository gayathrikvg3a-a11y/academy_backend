from django.urls import path

from .views import InternshipStudentAPIView, VacancyAPIView

urlpatterns = [
    path(
        "internship-students/",
        InternshipStudentAPIView.as_view(),
        name="internship-student-list",
    ),
    path(
        "internship-students/<int:pk>/",
        InternshipStudentAPIView.as_view(),
        name="internship-student-detail",
    ),

    path("vacancies/", VacancyAPIView.as_view()),
    path("vacancies/<int:pk>/", VacancyAPIView.as_view()),
]