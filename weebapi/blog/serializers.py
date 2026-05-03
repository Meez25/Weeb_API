from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.

    Handles the conversion between Post instances and their JSON
    representations.
    Adds a computed `url` field for direct API access to individual posts.
    """

    url = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        """
        Meta configuration for PostSerializer.

        Attributes:
            model (Post): The model being serialized.
            fields (list): Fields to include in the serialized output.
            read_only_fields (list): Fields that cannot be modified through the
            API.
        """

        model = Post
        fields = [
            "url", "id", "title", "slug", "excerpt", "content",
            "category", "readTime", "author", "is_published",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "slug", "author", "created_at", "updated_at"]

    def get_url(self, obj):
        """
        Build the absolute URL for a given Post instance.

        Uses the current request context to generate a full API URL
        (e.g., `https://example.com/api/posts/my-post-slug/`).

        Args:
            obj (Post): The Post instance being serialized.

        Returns:
            str: The absolute URL to access the post detail endpoint.
        """
        request = self.context.get('request')
        return request.build_absolute_uri(f"/api/posts/{obj.slug}/")

    def get_author(self, obj):
        """
        Return the full name of the author or 'Anonyme' if no author.

        Never falls back to email — that would leak PII on the public list
        endpoint and let anonymous users enumerate registered accounts.
        """
        if obj.author:
            full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
            return full_name or "Anonyme"
        return "Anonyme"
