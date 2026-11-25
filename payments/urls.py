from django.urls import path

from .views import (
    PaymentAPIView,
    PaymentSlipAPIView,
)

urlpatterns = [
    path("payments/",PaymentAPIView.as_view(),),
    path("payments/<int:pk>/",PaymentAPIView.as_view(),),
    path("payments/<int:pk>/payment-slip/",PaymentSlipAPIView.as_view(),),
]