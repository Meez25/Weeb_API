from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Contact model.

    Provides a clear and manageable view of contact form submissions
    within the Django admin dashboard.

    Features:
        - Displays key fields in the list view (first name, last name,
          email, phone, message, created date)
        - Enables filtering by creation date
        - Allows searching by all main contact fields
        - Orders submissions by most recent first
        - Marks 'created_at' as read-only to prevent modification
    """

    list_display = ("first_name", "last_name", "email_address",
                    "phone_number", "message", "created_at")
    list_filter = ("created_at",)
    search_fields = ("first_name", "last_name",
                     "email_address", "phone_number", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
