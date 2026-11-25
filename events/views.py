from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from students.permissions import UserPermission
from .pagination import get_paginator_class
from .models import Announcement, Event
from .serializers import AnnouncementSerializer, EventSerializer


class EventAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_event",
        "POST": "add_event",
        "PUT": "change_event",
        "PATCH": "change_event",
        "DELETE": "delete_event",
    }

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):

        if pk:
            event = get_object_or_404(Event,pk=pk,)
            serializer = EventSerializer(event,context={"request": request},)
            return Response(serializer.data)

        queryset = Event.objects.all().order_by("-event_date")

        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true"
            )

        data = request.query_params.get("data")
        if data == "alllist":
            serializer = EventSerializer(
                queryset,
                many=True,
                context={"request": request},
            )
            return Response(serializer.data)

        paginator = get_paginator_class(request)()
        page = paginator.paginate_queryset(queryset,request,)
        serializer = EventSerializer(page,many=True,context={"request": request},)
        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        return self.patch(request, pk)

    def patch(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AnnouncementAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_announcement",
        "POST": "add_announcement",
        "PUT": "change_announcement",
        "PATCH": "change_announcement",
        "DELETE": "delete_announcement",
    }

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):

        if pk:
            announcement = get_object_or_404(Announcement,pk=pk,)
            serializer = AnnouncementSerializer(announcement,context={"request": request},)
            return Response(serializer.data)

        queryset = Announcement.objects.filter(
            is_active=True
        ).order_by("-published_at")

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                title__icontains=search
            )

        is_important = request.query_params.get("is_important")
        if is_important:
            queryset = queryset.filter(
                is_important=is_important.lower() == "true"
            )

        data = request.query_params.get("data")
        if data == "alllist":
            serializer = AnnouncementSerializer(
                queryset,
                many=True,
                context={"request": request},
            )
            return Response(serializer.data)

        paginator = get_paginator_class(request)()
        page = paginator.paginate_queryset(queryset,request,)
        serializer = AnnouncementSerializer(
            page,
            many=True,
            context={"request": request},
        )
        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):

        serializer = AnnouncementSerializer(data=request.data,)
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
        announcement = get_object_or_404(Announcement,pk=pk,)
        serializer = AnnouncementSerializer(announcement,data=request.data,partial=True,)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk=None):

        announcement = get_object_or_404(Announcement,pk=pk,)
        announcement.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )