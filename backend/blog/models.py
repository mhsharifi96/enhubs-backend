from django.db import models
from django.utils.text import slugify


def unique_slugify(instance: models.Model, value: str, slug_field_name: str = "slug"):
    """Create a unique slug for the given model instance."""
    base_slug = slugify(value) or "item"
    slug = base_slug
    ModelClass = instance.__class__
    counter = 1

    while (
        ModelClass.objects.filter(**{slug_field_name: slug})
        .exclude(pk=instance.pk)
        .exists()
    ):
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class SeoFields(models.Model):
    """Reusable SEO metadata fields."""

    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        abstract = True


class Category(SeoFields):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Post(SeoFields):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True,null=True)
    content = models.TextField()
    category = models.ForeignKey(
        Category, related_name="posts", on_delete=models.CASCADE,
        null=True, blank=True
    )
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)
