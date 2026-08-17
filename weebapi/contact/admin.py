from django.contrib import admin

from .models import Contact


class SatisfactionFilter(admin.SimpleListFilter):
    """Sidebar filter that labels the binary satisfaction score."""

    title = "satisfaction"
    parameter_name = "satisfaction"

    def lookups(self, request, model_admin):
        return (("1", "Positif"), ("0", "Négatif"))

    def queryset(self, request, queryset):
        if self.value() in ("0", "1"):
            return queryset.filter(satisfaction=self.value())
        return queryset


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Contact model.

    Provides a clear and manageable view of contact form submissions
    within the Django admin dashboard.

    Features:
        - Displays key fields in the list view (first name, last name,
          email, phone, satisfaction score, message, created date)
        - Enables filtering by creation date and satisfaction score
        - Allows searching by all main contact fields
        - Orders submissions by most recent first
        - Marks 'created_at' as read-only to prevent modification
    """

    @admin.display(description="Satisfaction", ordering="satisfaction")
    def satisfaction_label(self, obj):
        """Render the raw 0/1 score as a human-readable label."""
        if obj.satisfaction is None:
            return "—"
        return "Positif" if obj.satisfaction == 1 else "Négatif"

    list_display = ("first_name", "last_name", "email_address",
                    "phone_number", "satisfaction_label", "message",
                    "created_at")
    list_filter = ("created_at", SatisfactionFilter)
    search_fields = ("first_name", "last_name",
                     "email_address", "phone_number", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
