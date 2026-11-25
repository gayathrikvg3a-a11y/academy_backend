from django.contrib import admin
from .models import Enquiry, CallHistory, EnquiryNew


class CallHistoryInline(admin.TabularInline):
    model = CallHistory
    extra = 0


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):

    list_display = (
        'student_name',
        'phone',
        'course',
        'enquiry_stage',
        'responsible_person',
        'is_converted',
        'enquiry_date',
    )

    list_filter = (
        'enquiry_stage',
        'is_converted',
        'course',
    )

    search_fields = (
        'student_name',
        'phone',
        'college',
    )

    inlines = [CallHistoryInline]


@admin.register(CallHistory)
class CallHistoryAdmin(admin.ModelAdmin):

    list_display = (
        'enquiry',
        'call_status',
        'called_by',
        'call_date',
        'next_follow_up_date',
    )

    list_filter = (
        'call_status',
        'call_date',
    )

admin.site.register(EnquiryNew)