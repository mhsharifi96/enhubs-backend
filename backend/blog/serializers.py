from rest_framework import serializers

from .models import Category, Post, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "meta_title",
            "meta_description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {"slug": {"required": False}}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "slug",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {"slug": {"required": False}}


class PostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    tags = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Tag.objects.all(),
        many=True,
        required=False,
        default=list,
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "content",
            "category",
            "tags",
            "is_published",
            "meta_title",
            "meta_description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {
            "slug": {"required": False},
            "tags": {"default": []},
        }
