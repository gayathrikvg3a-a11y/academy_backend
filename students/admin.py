from django.contrib import admin
from . models import Staff, Student
from .models import PaymentType, FeeType
# Register your models here.
admin.site.register(Student)
admin.site.register(Staff)
@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'payment_type_name',
        'is_active',
        'created_at',
    )

    list_filter = ('is_active',)

    search_fields = ('payment_type_name',)