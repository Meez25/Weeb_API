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
            "author", "is_published", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def validate_title(self, value):
        """
        Basic validation: trim and ensure non-empty title.
        Args:
            value (str): The title value to validate.
        """
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value    

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
