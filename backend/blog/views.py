from rest_framework import filters, viewsets

from .models import Category, Post, Tag
from .serializers import CategorySerializer, PostSerializer, TagSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "slug", "description", "meta_title", "meta_description")
    ordering_fields = ("name", "created_at", "updated_at")


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "slug"
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "slug")
    ordering_fields = ("name", "created_at", "updated_at")


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    serializer_class = PostSerializer
    lookup_field = "slug"
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "meta_title",
        "meta_description",
    )
    ordering_fields = (
        "created_at",
        "updated_at",
        "title",
    )
