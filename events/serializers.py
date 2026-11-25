from rest_framework import serializers

from .models import Announcement, Event


class EventSerializer(serializers.ModelSerializer):
    banner_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "banner",
            "banner_url",
            "event_date",
            "event_time",
            "venue",
            "registration_link",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]

    def get_banner_url(self, obj):
        if not obj.banner:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.banner.url)

        return obj.banner.url


class AnnouncementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Announcement
        fields = "__all__"