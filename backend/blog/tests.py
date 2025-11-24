# Tests for blog API endpoints.
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Post, Tag


class BlogApiTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Programming")
        self.tag = Tag.objects.create(name="Django")

    def test_create_category_auto_slug(self):
        url = reverse("category-list")
        payload = {"name": "Web Development", "meta_description": "All about the web"}

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["slug"], "web-development")
        self.assertEqual(Category.objects.count(), 2)

    def test_create_post_with_tags(self):
        url = reverse("post-list")
        payload = {
            "title": "First Post",
            "excerpt": "Short summary",
            "content": "Full body content",
            "category": self.category.slug,
            "tags": [self.tag.slug],
            "is_published": True,
            "meta_title": "First Post Title",
            "meta_description": "Meta description for SEO.",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(pk=response.data["id"])
        self.assertEqual(post.slug, "first-post")
        self.assertTrue(post.tags.filter(pk=self.tag.pk).exists())
