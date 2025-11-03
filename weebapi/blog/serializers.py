from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "url", "id", "title", "slug", "excerpt", "content",
            "author", "is_published", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f"/api/posts/{obj.slug}/")
