from rest_framework import generics, permissions
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer


class PostListCreateView(generics.ListCreateAPIView):
    """
    API view for listing all published posts or creating a new one.

    - **GET**: Returns a list of all published posts.
        Supports optional filtering, searching, and ordering.
    - **POST**: Creates a new Post entry.

    ### Query Parameters
    - `q` (str, optional): Performs a text search in `title`, `excerpt`,
      `content`, and `author` fields. Case-insensitive.
      Example: `?q=python`
    - `author` (str, optional): Filters posts by author name.
      Example: `?author=Alice`
    - `ordering` (str, optional): Sorts results by creation date.
      Accepts:
        - `"created_at"` → oldest first
        - `"-created_at"` → newest first (default)
      Example: `?ordering=created_at`

    ### Permissions
    `AllowAny` — anyone (authenticated or not) can view and create posts.

    ### Example
        GET /api/posts/?q=django&author=John&ordering=created_at
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset().filter(is_published=True)

        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(excerpt__icontains=q)
                | Q(content__icontains=q)
                | Q(author__icontains=q)
            )

        author = self.request.query_params.get("author")
        if author:
            qs = qs.filter(author__icontains=author)

        ordering = self.request.query_params.get("ordering", "-created_at")
        if ordering not in ("created_at", "-created_at"):
            ordering = "-created_at"

        return qs.order_by(ordering)


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
