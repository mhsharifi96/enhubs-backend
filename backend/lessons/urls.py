# lessons/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AudioLessionViewSet

router = DefaultRouter()
router.register(r'lessons/audios', AudioLessionViewSet, basename='audio-lesson')

urlpatterns = [
    path("", include(router.urls)),
]
