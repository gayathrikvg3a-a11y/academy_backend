from django.contrib import admin
from .models import FeeType, PaymentMethod
# Register your models here.
admin.site.register(FeeType)
admin.site.register(PaymentMethod)
