from django.shortcuts import get_object_or_404

from rest_framework import filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
import os
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from students.permissions import UserPermission
from .models import (Album, Banner, GalleryEvent, GalleryItem)

from .serializers import (
    AlbumSerializer,
    BannerSerializer,
    GalleryEventSerializer,
    GalleryItemSerializer,
)


# ==========================================================
# GALLERY EVENT
# ==========================================================

class GalleryEventAPIView(APIView):

    def get(self, request, pk=None):

        if pk:
            event = get_object_or_404(GalleryEvent, pk=pk)
            serializer = GalleryEventSerializer(event)
            return Response(serializer.data)

        queryset = GalleryEvent.objects.all()

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )

        ordering = request.query_params.get("ordering")
        if ordering in ["from_date", "-from_date", "created_at", "-created_at"]:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-from_date")

        serializer = GalleryEventSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):

        serializer = GalleryEventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):

        event = get_object_or_404(GalleryEvent, pk=pk)

        serializer = GalleryEventSerializer(
            event,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):

        event = get_object_or_404(GalleryEvent, pk=pk)
        event.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================================
# ALBUM
# ==========================================================

class AlbumAPIView(APIView):

    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_album",
        "POST": "add_album",
        "PUT": "change_album",
        "PATCH": "change_album",
        "DELETE": "delete_album",
    }
    

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):

        if pk:
            album = get_object_or_404(
                Album.objects.prefetch_related("gallery_items"),
                pk=pk,
            )

            serializer = AlbumSerializer(
                album,
                context={"request": request},
            )
            return Response(serializer.data)

        queryset = Album.objects.prefetch_related("gallery_items")

        # Return only album id and title
        data = request.query_params.get("data")
        if data == "idname":
            queryset = queryset.filter(is_active=True).order_by("display_order")

            return Response([
                {
                    "id": album.id,
                    "title": album.title,
                }
                for album in queryset
            ])

        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true"
            )

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering")
        allowed = [
            "display_order",
            "-display_order",
            "created_at",
            "-created_at",
            "title",
            "-title",
        ]

        if ordering in allowed:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("display_order")

        serializer = AlbumSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = AlbumSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):

        album = get_object_or_404(Album, pk=pk)

        serializer = AlbumSerializer(
            album,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk=None):

        album = get_object_or_404(Album, pk=pk)

        album.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================================
# GALLERY ITEM
# ==========================================================

class GalleryItemAPIView(APIView):


    def get(self, request, pk=None):

        # Get a single gallery item by ID
        if pk:
            item = get_object_or_404(
                GalleryItem.objects.select_related("album"),
                pk=pk,
            )

            serializer = GalleryItemSerializer(
                item,
                context={"request": request},
            )

            return Response(serializer.data)

        # Get one album with all its gallery items
        album_id = request.query_params.get("album")
        if album_id:
            album = get_object_or_404(
                Album.objects.prefetch_related("gallery_items"),
                pk=album_id,
            )

            serializer = AlbumSerializer(
                album,
                context={"request": request},
            )

            return Response(serializer.data)

        # Get all gallery items
        queryset = GalleryItem.objects.select_related("album")

        media_type = request.query_params.get("media_type")
        if media_type:
            queryset = queryset.filter(media_type=media_type)

        is_featured = request.query_params.get("is_featured")
        if is_featured is not None:
            queryset = queryset.filter(
                is_featured=is_featured.lower() == "true"
            )

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(caption__icontains=search) |
                Q(album__title__icontains=search)
            )

        ordering = request.query_params.get("ordering")
        allowed = [
            "display_order",
            "-display_order",
            "created_at",
            "-created_at",
        ]

        if ordering in allowed:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("display_order")

        serializer = GalleryItemSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

    def post(self, request):
        media_files = request.FILES.getlist("file")
        thumbnail = request.FILES.get("thumbnail")  # Optional

        if not media_files:
            return Response(
                {"message": "No media files provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_items = []

        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"]

        for media_file in media_files:
            data = {
                "album": request.data.get("album"),
                "caption": request.data.get("caption", ""),
                "is_featured": request.data.get("is_featured", False),
                "display_order": request.data.get("display_order", 0),
                "file": media_file,
            }

            content_type = media_file.content_type or ""
            extension = os.path.splitext(media_file.name)[1].lower()

            if content_type.startswith("image/") or extension in image_extensions:
                data["media_type"] = GalleryItem.IMAGE

            elif content_type.startswith("video/") or extension in video_extensions:
                data["media_type"] = GalleryItem.VIDEO

                # Thumbnail is optional
                if thumbnail:
                    data["thumbnail"] = thumbnail

            else:
                return Response(
                    {
                        "message": f"{media_file.name} is not a supported image/video format."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = GalleryItemSerializer(
                data=data,
                context={"request": request},
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            created_items.append(serializer.data)

        return Response(
            {
                "message": f"{len(created_items)} media files uploaded successfully.",
                "data": created_items,
            },
            status=status.HTTP_201_CREATED,
        )
    # def post(self, request):

    #     serializer = GalleryItemSerializer(
    #         data=request.data,
    #         context={"request": request},
    #     )

    #     if serializer.is_valid():
    #         serializer.save()

    #         return Response(
    #             serializer.data,
    #             status=status.HTTP_201_CREATED,
    #         )

    #     return Response(
    #         serializer.errors,
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):

        item = get_object_or_404(GalleryItem, pk=pk)

        serializer = GalleryItemSerializer(
            item,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk=None):

        item = get_object_or_404(GalleryItem, pk=pk)

        item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



class BannerAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_banner",
        "POST": "add_banner",
        "PUT": "change_banner",
        "PATCH": "change_banner",
        "DELETE": "delete_banner",
    }

    parser_classes = (MultiPartParser, FormParser)

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):
        # Single Banner
        if pk:
            banner = get_object_or_404(Banner, pk=pk)
            serializer = BannerSerializer(banner)
            return Response(serializer.data)

        # All Banners
        banners = Banner.objects.all().order_by("-created_at")
        serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BannerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Banner added successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk):
        banner = get_object_or_404(Banner, pk=pk)

        serializer = BannerSerializer(
            banner,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Banner updated successfully.",
                    "data": serializer.data,
                }
            )

        return Response(
            {
                "status": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        banner = get_object_or_404(Banner, pk=pk)
        banner.delete()

        return Response(
            {
                "status": True,
                "message": "Banner deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class PublicAlbumAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):

        if pk:
            album = get_object_or_404(
                Album.objects.filter(is_active=True).prefetch_related("gallery_items"),
                pk=pk,
            )

            serializer = AlbumSerializer(
                album,
                context={"request": request},
            )
            return Response(serializer.data)

        queryset = Album.objects.filter(is_active=True).prefetch_related("gallery_items")

        data = request.query_params.get("data")
        if data == "idname":
            queryset = queryset.order_by("display_order")

            return Response([
                {
                    "id": album.id,
                    "title": album.title,
                }
                for album in queryset
            ])

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        ordering = request.query_params.get("ordering")
        allowed = [
            "display_order",
            "-display_order",
            "created_at",
            "-created_at",
            "title",
            "-title",
        ]

        queryset = queryset.order_by(ordering if ordering in allowed else "display_order")

        serializer = AlbumSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)