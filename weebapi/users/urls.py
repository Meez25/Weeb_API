from django.urls import path
from .views import create_user, me


urlpatterns = [
    path("users/create/", create_user),
    path("users/me/", me)
]
