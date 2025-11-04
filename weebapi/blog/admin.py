from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Post model.

    Defines how Post instances appear and can be managed
    in the Django admin dashboard.

    Features:
        - Displays key fields in the list view (title, publication status,
          creation date)
        - Enables filtering and search capabilities
        - Automatically prepopulates the slug field from the title
    """

    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "content", "author")
    prepopulated_fields = {"slug": ("title",)}
