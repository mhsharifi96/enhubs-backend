from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from blog.models import Category, Post, Tag
from blog.serializers import CategorySerializer, PostSerializer, TagSerializer, SinglePostSerializer
from blog.filters import PostFilter

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
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SinglePostSerializer
        return PostSerializer
    
    lookup_field = "slug"
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend,)
    search_fields = (
        "title",
        "slug",
        "excerpt",
    )
    ordering_fields = (
        "created_at",
        "updated_at",
        "title",
    )
    filterset_class = PostFilter

