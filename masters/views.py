from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from events.pagination import get_paginator_class

from .models import (
    FeeType,
    PaymentMethod,
    Batch,
)

from .serializers import (
    FeeTypeSerializer,
    PaymentMethodSerializer
)


# ==========================================================
# FEE TYPE
# ==========================================================

class FeeTypeAPIView(APIView):

    def get(self, request, pk=None):

        if pk:
            fee_type = get_object_or_404(FeeType, pk=pk)
            serializer = FeeTypeSerializer(fee_type)
            return Response(serializer.data)

        queryset = FeeType.objects.all()
        serializer = FeeTypeSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):

        serializer = FeeTypeSerializer(data=request.data)

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

        fee_type = get_object_or_404(FeeType, pk=pk)

        serializer = FeeTypeSerializer(
            fee_type,
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

        fee_type = get_object_or_404(FeeType, pk=pk)
        fee_type.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


# ==========================================================
# PAYMENT METHOD
# ==========================================================

class PaymentMethodAPIView(APIView):
    def get(self, request, pk=None):

        if pk:
            payment_method = get_object_or_404(PaymentMethod, pk=pk)
            serializer = PaymentMethodSerializer(payment_method)
            return Response(serializer.data)

        queryset = PaymentMethod.objects.all().order_by("-id")
        # Return all data without pagination
        if request.query_params.get("data") == "alllist":
            serializer = PaymentMethodSerializer(queryset, many=True)
            return Response(serializer.data)

        # Use your existing pagination utility
        paginator_class = get_paginator_class(request)
        paginator = paginator_class()

        page = paginator.paginate_queryset(queryset, request)

        serializer = PaymentMethodSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):

        serializer = PaymentMethodSerializer(
            data=request.data,
        )

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

        payment_method = get_object_or_404(
            PaymentMethod,
            pk=pk,
        )

        serializer = PaymentMethodSerializer(
            payment_method,
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

        payment_method = get_object_or_404(
            PaymentMethod,
            pk=pk,
        )

        payment_method.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

