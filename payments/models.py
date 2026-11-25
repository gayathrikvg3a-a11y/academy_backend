from django.conf import settings
from django.db import models

from students.models import Student
from masters.models import PaymentMethod


class Payment(models.Model):

    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    payment_date = models.DateField()

    collection_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collected_payments'
    )

    transaction_reference = models.CharField(
        max_length=150,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.receipt_number:
            last_payment = Payment.objects.order_by('id').last()

            if last_payment:
                next_id = last_payment.id + 1
            else:
                next_id = 1

            self.receipt_number = f"CIG-PAY-{next_id:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} - {self.student.student_name}"