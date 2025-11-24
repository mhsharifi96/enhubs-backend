from blog.models import Post
import django_filters


class PostFilter(django_filters.FilterSet):
    category_slug = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="iexact"
    )
    tags_slug = django_filters.CharFilter(
        field_name="tags__slug", lookup_expr="iexact"
    )

    class Meta:
        model = Post
        fields = ["category_slug", "tags_slug"]