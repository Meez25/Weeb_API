from django.db.models import Q
from rest_framework import generics, permissions

from .models import Post
from .permissions import IsOwnerOrReadOnly
from .serializers import PostSerializer


class PostListCreateView(generics.ListCreateAPIView):
    """
    API view for listing all published posts or creating a new one.

    - **GET**: Returns a list of all published posts.
        Supports optional filtering, searching, and ordering.
    - **POST**: Creates a new Post entry. Author is automatically set to the
        authenticated user.

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
    - GET: `AllowAny` — anyone can view posts
    - POST: `IsAuthenticated` — only authenticated users can create posts

    ### Example
        GET /api/posts/?q=django&author=John&ordering=created_at
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        """
        Allow anyone to list posts (GET), but require authentication to create (POST).

        IsOwnerOrReadOnly is intentionally NOT applied to POST: there is no
        existing object yet, so object-level checks are a no-op. Object-level
        ownership is enforced on the retrieve/update/destroy view instead.
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset().filter(is_published=True)

        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(excerpt__icontains=q)
                | Q(content__icontains=q)
                | Q(author__first_name__icontains=q)
                | Q(author__last_name__icontains=q)
            )

        author = self.request.query_params.get("author")
        if author:
            qs = qs.filter(
                Q(author__first_name__icontains=author)
                | Q(author__last_name__icontains=author)
            )

        ordering = self.request.query_params.get("ordering", "-created_at")
        if ordering not in ("created_at", "-created_at"):
            ordering = "-created_at"

        return qs.order_by(ordering)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a single Post.

    - GET: Returns a single Post by its slug. Anyone can view.
    - PUT/PATCH: Updates the specified Post. Requires authentication.
    - DELETE: Removes the Post from the database. Requires authentication.

    Lookup:
        Uses the `slug` field for URL identification instead of the default
        `id`.

    Permissions:
        - GET: `AllowAny` — anyone can view posts
        - PUT/PATCH/DELETE: `IsAuthenticated` — only authenticated users can modify
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = "slug"  # Identify using "slug" in the URL

    def get_permissions(self):
        """
        Allow anyone to retrieve posts (GET), but require authentication to update or delete.
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
