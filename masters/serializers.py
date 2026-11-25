from rest_framework import serializers

from .models import (
    FeeType,
    PaymentMethod
)


class FeeTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeeType
        fields = '__all__'


class PaymentMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMethod
        fields = '__all__'


