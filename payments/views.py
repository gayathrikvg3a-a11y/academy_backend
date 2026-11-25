from io import BytesIO

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from students.permissions import UserPermission

from .models import Payment
from .serializers import PaymentSerializer


# ==========================================================
# PAYMENT
# ==========================================================

class PaymentAPIView(APIView):
    permission_classes = [UserPermission]

    permission_map = {
        "GET": "view_payment",
        "POST": "add_payment",
        "PUT": "change_payment",
        "PATCH": "change_payment",
        "DELETE": "delete_payment",
    }

    def initial(self, request, *args, **kwargs):
        self.permission_codename = self.permission_map.get(request.method)
        super().initial(request, *args, **kwargs)

    def get(self, request, pk=None):

        if pk:
            payment = get_object_or_404(
                Payment.objects.select_related(
                    "student",
                    "student__course",
                    "payment_method",
                    "collection_staff",
                ),
                pk=pk,
            )

            serializer = PaymentSerializer(payment)

            return Response(serializer.data)

        queryset = Payment.objects.select_related(
            "student",
            "student__course",
            "payment_method",
            "collection_staff",
        ).order_by("-created_at")

        # Filters

        student = request.query_params.get("student")
        if student:
            queryset = queryset.filter(student=student)

        payment_method = request.query_params.get("payment_method")
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        collection_staff = request.query_params.get("collection_staff")
        if collection_staff:
            queryset = queryset.filter(collection_staff=collection_staff)

        payment_date = request.query_params.get("payment_date")
        if payment_date:
            queryset = queryset.filter(payment_date=payment_date)

        # Search

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                receipt_number__icontains=search
            ) | queryset.filter(
                student__student_id__icontains=search
            ) | queryset.filter(
                student__student_name__icontains=search
            ) | queryset.filter(
                transaction_reference__icontains=search
            )

        # Ordering

        ordering = request.query_params.get("ordering")

        allowed = [
            "payment_date",
            "-payment_date",
            "amount",
            "-amount",
            "created_at",
            "-created_at",
        ]

        if ordering in allowed:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-created_at")

        serializer = PaymentSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = PaymentSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save(
                collection_staff=request.user,
            )

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

        payment = get_object_or_404(
            Payment,
            pk=pk,
        )

        serializer = PaymentSerializer(
            payment,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk=None):

        payment = get_object_or_404(
            Payment,
            pk=pk,
        )

        payment.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


# ==========================================================
# PAYMENT SLIP
# ==========================================================

class PaymentSlipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        payment = get_object_or_404(
            Payment.objects.select_related(
                "student",
                "student__course",
                "payment_method",
                "collection_staff",
            ),
            pk=pk,
        )

        student = payment.student

        total_paid = (
            student.payments.aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        balance = student.course_fee - total_paid

        buffer = BytesIO()

        pdf = canvas.Canvas(
            buffer,
            pagesize=A5,
        )

        width, height = A5

        pdf.setTitle(payment.receipt_number)

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(
            width / 2,
            height - 22 * mm,
            "CIGNES ACADEMY",
        )

        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(
            width / 2,
            height - 29 * mm,
            "Payment Receipt",
        )

        y = height - 42 * mm

        rows = [
            ("Receipt Number", payment.receipt_number),
            ("Student ID", student.student_id),
            ("Student Name", student.student_name),
            ("Course", student.course.name if student.course else "-"),
            ("Payment Date", str(payment.payment_date)),
            ("Payment Method", payment.payment_method.name),
            ("Transaction Ref", payment.transaction_reference or "-"),
            (
                "Collected By",
                payment.collection_staff.username
                if payment.collection_staff
                else "-",
            ),
        ]

        for label, value in rows:

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(18 * mm, y, f"{label}:")

            pdf.setFont("Helvetica", 10)
            pdf.drawString(65 * mm, y, str(value))

            y -= 8 * mm

        pdf.line(
            18 * mm,
            y,
            width - 18 * mm,
            y,
        )

        y -= 12 * mm

        pdf.setFont("Helvetica-Bold", 11)

        pdf.drawString(
            18 * mm,
            y,
            f"Payment Amount : ₹ {payment.amount}",
        )

        y -= 9 * mm

        pdf.drawString(
            18 * mm,
            y,
            f"Course Fee : ₹ {student.course_fee}",
        )

        y -= 9 * mm

        pdf.drawString(
            18 * mm,
            y,
            f"Total Paid : ₹ {total_paid}",
        )

        y -= 9 * mm

        pdf.drawString(
            18 * mm,
            y,
            f"Balance : ₹ {balance}",
        )

        y -= 20 * mm

        pdf.setFont("Helvetica", 9)

        pdf.drawCentredString(
            width / 2,
            y,
            "Thank you for choosing CIGNES Academy.",
        )

        pdf.showPage()
        pdf.save()

        buffer.seek(0)

        return FileResponse(
            buffer,
            as_attachment=False,
            filename=f"{payment.receipt_number}.pdf",
        )