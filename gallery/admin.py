from django.contrib import admin
from django.utils.html import format_html

from .models import (
    GalleryEvent,
    Album,
    GalleryItem,
)


# ==========================================================
# GALLERY EVENT
# ==========================================================

@admin.register(GalleryEvent)
class GalleryEventAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "from_date",
        "to_date",
        "image_preview",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "from_date",
        "to_date",
    )

    readonly_fields = (
        "created_at",
        "image_preview",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="120" style="border-radius:8px;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Preview"


# ==========================================================
# GALLERY ITEM INLINE
# ==========================================================

class GalleryItemInline(admin.TabularInline):
    model = GalleryItem
    extra = 1


# ==========================================================
# ALBUM
# ==========================================================

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "cover_preview",
        "is_active",
        "display_order",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    ordering = (
        "display_order",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "cover_preview",
    )

    inlines = [
        GalleryItemInline,
    ]

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="120" style="border-radius:8px;" />',
                obj.cover_image.url,
            )
        return "-"

    cover_preview.short_description = "Cover"


# ==========================================================
# GALLERY ITEM
# ==========================================================

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):

    list_display = (
        "album",
        "media_type",
        "preview",
        "is_featured",
        "display_order",
        "created_at",
    )

    list_filter = (
        "media_type",
        "is_featured",
    )

    search_fields = (
        "caption",
        "album__title",
    )

    ordering = (
        "display_order",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "preview",
    )

    def preview(self, obj):

        if not obj.file:
            return "-"

        if obj.media_type == "IMAGE":
            return format_html(
                '<img src="{}" width="120" style="border-radius:8px;" />',
                obj.file.url,
            )

        return format_html(
            '<a href="{}" target="_blank">View Video</a>',
            obj.file.url,
        )

    preview.short_description = "Preview"