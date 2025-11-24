from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog.views import CategoryViewSet, PostViewSet, TagViewSet


router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path('', include(router.urls)),
]
