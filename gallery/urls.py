from django.urls import path

from .views import (
    AlbumAPIView,
    BannerAPIView,
    GalleryEventAPIView,
    GalleryItemAPIView,
    PublicAlbumAPIView,
)

urlpatterns = [
    # Album
    path(
        "albums/",
        AlbumAPIView.as_view(),
        name="album-list",
    ),
    path(
        "albums/<int:pk>/",
        AlbumAPIView.as_view(),
        name="album-detail",
    ),

    # Gallery Item
    path(
        "gallery-items/",
        GalleryItemAPIView.as_view(),
        name="gallery-item-list",
    ),
    path(
        "gallery-items/<int:pk>/",
        GalleryItemAPIView.as_view(),
        name="gallery-item-detail",
    ),

    # Gallery Event
    path(
        "gallery-events/",
        GalleryEventAPIView.as_view(),
        name="gallery-event-list",
    ),
    path(
        "gallery-events/<int:pk>/",
        GalleryEventAPIView.as_view(),
        name="gallery-event-detail",
    ),

    path("banners/", BannerAPIView.as_view(), name="banner-list-create"),
    path("banners/<int:pk>/", BannerAPIView.as_view(), name="banner-detail"),

    path("albums-public/", PublicAlbumAPIView.as_view()),
    path("albums-public/<int:pk>/", PublicAlbumAPIView.as_view()),

]