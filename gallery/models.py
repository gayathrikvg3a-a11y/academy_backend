from django.db import models


# ==========================================================
# GALLERY EVENT (Legacy)
# ==========================================================

class GalleryEvent(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True                                          
    )

    from_date = models.DateField()

    to_date = models.DateField()

    image = models.ImageField(
        upload_to="gallery/events/images/",
        blank=True,
        null=True,
    )

    video = models.FileField(
        upload_to="gallery/events/videos/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-from_date"]
        verbose_name = "Gallery Event"
        verbose_name_plural = "Gallery Events"

    def __str__(self):
        return self.title


# ==========================================================
# ALBUM
# ==========================================================

class Album(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    cover_image = models.ImageField(
        upload_to="gallery/albums/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "display_order",
            "-created_at",
        ]

        verbose_name = "Album"
        verbose_name_plural = "Albums"

    def __str__(self):
        return self.title


# ==========================================================
# GALLERY ITEM
# ==========================================================

class GalleryItem(models.Model):

    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

    MEDIA_TYPES = (
        (IMAGE, "Image"),
        (VIDEO, "Video"),
    )

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="gallery_items",
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPES,
        default=IMAGE,
    )

    file = models.FileField(
        upload_to="gallery/items/"
    )
    thumbnail = models.ImageField(upload_to="gallery/thumbnails/", null=True, blank=True)

    caption = models.CharField(
        max_length=255,
        blank=True
    )

    is_featured = models.BooleanField(
        default=False
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "display_order",
            "-created_at",
        ]

        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"

    def __str__(self):
        return f"{self.album.title} - {self.get_media_type_display()}"


class GalleryFile(models.Model):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

    MEDIA_TYPES = (
        (IMAGE, "Image"),
        (VIDEO, "Video"),
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(upload_to="gallery/files/")
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPES
    )

    caption = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["display_order", "-created_at"]
      
    def __str__(self):
        return f"{self.album.title} - {self.media_type}"


class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="banners/")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title