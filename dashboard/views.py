from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from batch.models import Batch
from courses.models import Course
from enquiries.models import Enquiry
from events.models import Event
from gallery.models import GalleryItem
from internships.models import InternshipStudent
from payments.models import Payment
from students.models import Student


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        total_collection = (
            Payment.objects.aggregate(total=Sum("amount"))["total"] or 0
        )

        data = {
            "total_students": Student.objects.count(),
            "total_courses": Course.objects.count(),
            "total_batches": Batch.objects.count(),
            "total_enquiries": Enquiry.objects.count(),
            "total_events": Event.objects.count(),
            "total_gallery_items": GalleryItem.objects.count(),
            "total_internships": InternshipStudent.objects.count(),
            "total_payments": Payment.objects.count(),
            "total_collection": total_collection,
        }

        return Response(data)