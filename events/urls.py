from django.urls import path

from .views import AnnouncementAPIView, EventAPIView

urlpatterns = [
    path("events/",EventAPIView.as_view(),name="event-list",),
    path("events/<int:pk>/",EventAPIView.as_view(),name="event-detail",),
    path("announcements/",AnnouncementAPIView.as_view(),name="announcement-list",),
    path("announcements/<int:pk>/",AnnouncementAPIView.as_view(),name="announcement-detail",),
]