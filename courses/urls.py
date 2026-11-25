from django.urls import path

from .views import (
    AcademicInternshipAPIView,
    BlogAPIView,
    CaseStudyAPIView,
    ContactInformationAPIView,
    CourseAPIView,
    CourseCategoryAPIView,
    CourseFeeOptionAPIView,
    CourseListAPIView,
    CurriculumModuleAPIView,
    CurriculumTopicAPIView,
    IndustryInternshipAPIView,
    LessonAPIView,
    LifeAtCignesAPIView,
    SelectAcademicInternshipAPIView,
    SelectIndustryInternshipAPIView,
    SelectLifeAtCignesAPIView,
    SelectedAcademicInternshipAPIView,
    SelectedIndustryInternshipAPIView,
    SelectedLifeAtCignesAPIView,
)

urlpatterns = [
    path("courses/", CourseAPIView.as_view(), name="course-list-create"),
    path("courses/<int:pk>/", CourseAPIView.as_view(), name="course-detail"),
    path("curriculum-modules/", CurriculumModuleAPIView.as_view(), name="curriculum-module-list-create"),
    path("curriculum-modules/<int:pk>/", CurriculumModuleAPIView.as_view(), name="curriculum-module-detail"),
    path("curriculum-topics/", CurriculumTopicAPIView.as_view(), name="curriculum-topic-list-create"),
    path("curriculum-topics/<int:pk>/", CurriculumTopicAPIView.as_view(), name="curriculum-topic-detail"),
    path("lessons/", LessonAPIView.as_view(), name="lesson-list-create"),
    path("lessons/<int:pk>/", LessonAPIView.as_view(), name="lesson-detail"),
    path("courses/<int:course_id>/fee-options/",CourseFeeOptionAPIView.as_view(),),
    path("courses/<int:course_id>/fee-options/<int:pk>/",CourseFeeOptionAPIView.as_view(),name="course-fee-option-detail"),

    path("course-list/", CourseListAPIView.as_view()),
    path("course-list/<int:pk>/", CourseListAPIView.as_view()),

    path("blogs/", BlogAPIView.as_view()),
    path("blogs/<int:pk>/", BlogAPIView.as_view()),

    path("course-category/", CourseCategoryAPIView.as_view()),
    path("course-category/<int:pk>/", CourseCategoryAPIView.as_view()),

    path("life-at-cignes/",LifeAtCignesAPIView.as_view()),
    path("life-at-cignes/<int:pk>/",LifeAtCignesAPIView.as_view()),
    path("life-at-cignes-selected/",SelectedLifeAtCignesAPIView.as_view()),
    path("life-at-cignes-select/",SelectLifeAtCignesAPIView.as_view(),),

    path("contact-information/",ContactInformationAPIView.as_view()),
    path("contact-information/<int:pk>/",ContactInformationAPIView.as_view()),

    path("academic-internships/",AcademicInternshipAPIView.as_view()),
    path("academic-internships/<int:pk>/",AcademicInternshipAPIView.as_view()),
    path("academic-internships-select/",SelectAcademicInternshipAPIView.as_view()),
    path("academic-internships-selected/",SelectedAcademicInternshipAPIView.as_view()),

    path("industry-internships/",IndustryInternshipAPIView.as_view()),
    path("industry-internships/<int:pk>/",IndustryInternshipAPIView.as_view()),
    path("industry-internships-select/",SelectIndustryInternshipAPIView.as_view()),
    path("industry-internships-selected/",SelectedIndustryInternshipAPIView.as_view()),

    path("case-studies/",CaseStudyAPIView.as_view()),
    path("case-studies/<int:pk>/",CaseStudyAPIView.as_view()),

]



