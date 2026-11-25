from django.urls import path

from .views import (
    FeeTypeAPIView,
    PaymentMethodAPIView
)

urlpatterns = [
    # Fee Type
    path(
        "fee-types/",
        FeeTypeAPIView.as_view(),
        name="fee-type-list",
    ),
    path(
        "fee-types/<int:pk>/",
        FeeTypeAPIView.as_view(),
        name="fee-type-detail",
    ),

    # Payment Method
    path(
        "payment-methods/",
        PaymentMethodAPIView.as_view(),
        name="payment-method-list",
    ),
    path(
        "payment-methods/<int:pk>/",
        PaymentMethodAPIView.as_view(),
        name="payment-method-detail",
    ),

]