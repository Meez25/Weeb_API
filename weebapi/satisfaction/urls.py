# core/urls.py
from django.urls import path
from .views import SatisfactionAPIView

urlpatterns = [
    path("satisfaction/",
         SatisfactionAPIView.as_view(),
         name="satisfaction"),
]
