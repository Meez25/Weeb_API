from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer


class PostListCreateView(generics.ListCreateAPIView):
    """
    API view for listing all published posts or creating a new one.

    - GET: Returns a list of all Post instances.
    - POST: Creates a new Post entry.

    Permissions:
        AllowAny — anyone (authenticated or not) can view and create posts.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a single Post.

    - GET: Returns a single Post by its slug.
    - PUT/PATCH: Updates the specified Post.
    - DELETE: Removes the Post from the database.

    Lookup:
        Uses the `slug` field for URL identification instead of the default
        `id`.

    Permissions:
        AllowAny — anyone can view, edit, or delete posts.
        (In a real-world setup, this should typically be restricted.)
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = "slug"  # Identify using "slug" in the URL
    permission_classes = [permissions.AllowAny]
