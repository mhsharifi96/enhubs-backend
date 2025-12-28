# lessons/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AudioLessionViewSet, CategoryViewSet, TranslateAPIView , SpeakingLessonViewSet, LessonsSitemapAPIView

router = DefaultRouter()
router.register(r'lessons/audios', AudioLessionViewSet, basename='audio-lesson')
router.register(r'lessons/speaking', SpeakingLessonViewSet, basename='speaking-lesson')
router.register(r'categories', CategoryViewSet, basename='category')


urlpatterns = [
    path("", include(router.urls)),
    path("translate/", TranslateAPIView.as_view(), name="translate"),
    path("lessons/sitemap/", LessonsSitemapAPIView.as_view(), name="lessons-sitemap"),
]
