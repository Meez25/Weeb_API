from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email_address",
                    "phone_number", "message", "created_at")
    list_filter = ("created_at",)
    search_fields = ("first_name", "last_name",
                     "email_address", "phone_number", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
