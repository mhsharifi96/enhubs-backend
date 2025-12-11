from django.http import HttpResponse
from django.urls import reverse
from rest_framework import filters, permissions, viewsets
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from utils.sitemaps import build_sitemap_xml

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


class BlogSitemapAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        posts = (
            Post.objects.filter(is_published=True)
            .only("slug", "updated_at")
            .order_by("-updated_at")
        )
        urls = []

        for post in posts:
            loc = request.build_absolute_uri(
                reverse("post-detail", kwargs={"slug": post.slug})
            )
            lastmod = post.updated_at.isoformat() if post.updated_at else None
            urls.append({"loc": loc, "lastmod": lastmod})

        xml = build_sitemap_xml(urls)
        return HttpResponse(xml, content_type="application/xml")
