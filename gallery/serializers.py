from rest_framework import serializers

from .models import (
    Banner,
    GalleryEvent,
    Album,
    GalleryFile,
    GalleryItem,
)


# ==========================================================
# GALLERY EVENT
# ==========================================================

class GalleryEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = GalleryEvent
        fields = "__all__"

    def validate(self, attrs):

        from_date = attrs.get(
            "from_date",
            getattr(self.instance, "from_date", None),
        )

        to_date = attrs.get(
            "to_date",
            getattr(self.instance, "to_date", None),
        )

        if (
            from_date
            and to_date
            and to_date < from_date
        ):
            raise serializers.ValidationError(
                {
                    "to_date":
                    "To date cannot be before From date."
                }
            )

        return attrs


# ==========================================================
# GALLERY ITEM
# ==========================================================

class GalleryItemSerializer(serializers.ModelSerializer):

    file = serializers.FileField(
        required=False,
        allow_null=True,
    )

    thumbnail = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    album_title = serializers.CharField(
        source="album.title",
        read_only=True,
    )

    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()   # ✅ Add this

    class Meta:
        model = GalleryItem
        fields = [
            "id",
            "album",
            "album_title",
            "media_type",
            "file",
            "file_url",
            "thumbnail",       # ✅ Include thumbnail field
            "thumbnail_url",   # ✅ Include thumbnail URL
            "caption",
            "is_featured",
            "display_order",
            "created_at",
            "updated_at",
        ]

        read_only_fields = (
            "created_at",
            "updated_at",
        )

    def get_file_url(self, obj):
        request = self.context.get("request")

        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url

        return None

    def get_thumbnail_url(self, obj):
        request = self.context.get("request")

        if obj.thumbnail:
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url

        return None

    def validate_file(self, value):

        if not value:
            return value

        max_size = 100 * 1024 * 1024   # 100 MB

        if value.size > max_size:
            raise serializers.ValidationError(
                "Maximum upload size is 100 MB."
            )

        return value


# ==========================================================
# ALBUM
# ==========================================================

class AlbumSerializer(serializers.ModelSerializer):
    gallery_items = GalleryItemSerializer(
        many=True,
        read_only=True,
    )

    total_items = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "description",
            "cover_image",
            "cover_image_url",
            "is_active",
            "display_order",
            "gallery_items",   # <-- nested media list
            "total_items",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        return obj.gallery_items.count()

    def get_cover_image_url(self, obj):
        request = self.context.get("request")
        if obj.cover_image:
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None


class GalleryFileSerializer(serializers.ModelSerializer):
    album_title = serializers.CharField(source="album.title", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryFile
        fields = [
            "id",
            "album",
            "album_title",
            "media_type",
            "file",
            "file_url",
            "caption",
            "is_featured",
            "display_order",
            "created_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = [
            "id",
            "title",
            "image",
            "created_at",
            "updated_at",
        ]