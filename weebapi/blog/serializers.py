from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "excerpt", "content",
            "author", "is_published", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]
