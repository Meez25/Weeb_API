from django.urls import path
from .views import PostListCreateView, PostRetrieveUpdateDestroyView

urlpatterns = [
    path("posts/", PostListCreateView.as_view(), name="post-list-create"),
    path("posts/<slug:slug>/", PostRetrieveUpdateDestroyView.as_view(), name="post-detail"),
]
