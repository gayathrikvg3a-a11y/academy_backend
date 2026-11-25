from decimal import Decimal

from django.db import models

from rest_framework import serializers

from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source='student.student_name',
        read_only=True
    )

    student_id = serializers.CharField(
        source='student.student_id',
        read_only=True
    )

    payment_method_name = serializers.CharField(
        source='payment_method.name',
        read_only=True
    )

    collection_staff_name = serializers.CharField(
        source='collection_staff.username',
        read_only=True
    )

    course_fee = serializers.DecimalField(
        source='student.course_fee',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_paid = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

        read_only_fields = [
            'receipt_number'
        ]

    def get_total_paid(self, obj):
        return obj.student.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def get_balance(self, obj):
        total_paid = obj.student.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        return obj.student.course_fee - total_paid

    def validate(self, attrs):

        student = attrs.get('student')
        amount = attrs.get('amount')

        if not student or amount is None:
            return attrs

        if amount <= 0:
            raise serializers.ValidationError({
                'amount': 'Payment amount must be greater than zero.'
            })

        total_paid = student.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        balance = student.course_fee - total_paid

        if amount > balance:
            raise serializers.ValidationError({
                'amount': f'Payment exceeds balance. Current balance is ₹{balance}.'
            })

        return attrs