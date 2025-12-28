from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse
from django.urls import reverse

from rest_framework import viewsets, mixins
from lessons.models import (
    Audio,
    Category,
    PostStatus,
    AudioHistory,
    Speaking,
    SpeakingStatus,
)
from lessons.serializers import (
    AudioSerializer,
    CategorySerializer,
    SpeakingListSerializer,
    SpeakingDetailSerializer,
)

from rest_framework.pagination import PageNumberPagination
from googletrans import Translator
from django.db.models import Q
from utils.sitemaps import build_sitemap_xml

import asyncio


class LessonPagination(PageNumberPagination):
    page_size = 10  # number of items per page
    page_size_query_param = "page_size"  # allow client to set page size
    max_page_size = 10  # maximum page size allowed


class AudioLessionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AudioSerializer
    pagination_class = LessonPagination

    def get_queryset(self):
        queryset = Audio.objects.filter(status=PostStatus.ENABLE).order_by(
            "-created_at"
        )

        params = self.request.query_params
        category_name = params.get("category")

        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        search = params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(transcript__icontains=search)
            )

        return queryset

    def get_permissions(self):
        """Authenticate only for retrieve endpoint."""
        # if self.action == 'retrieve':
        #     permission_classes = [permissions.IsAuthenticated]
        # else:
        permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().retrieve(request, *args, **kwargs)

        if request.user.is_authenticated:
            history, created = AudioHistory.objects.get_or_create(
                user=request.user, audio=instance
            )
            if not created:
                history.views_count += 1
                history.save(update_fields=["views_count", "updated_at"])

        return response


class SpeakingLessonViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = LessonPagination
    lookup_field = "slug"          # 👈 use slug instead of pk
    lookup_url_kwarg = "slug"      # 👈 optional but explicit

    def get_serializer_class(self):
        if self.action == "list":
            return SpeakingListSerializer  # 👈 serializer for list
        return SpeakingDetailSerializer  # 👈 serializer for retrieve

    def get_queryset(self):
        queryset = Speaking.objects.filter(status=SpeakingStatus.ENABLE).order_by(
            "-created_at"
        )

        params = self.request.query_params

        category_name = params.get("category")
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        search = params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(transcript__icontains=search)
            )

        return queryset


class CategoryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"


class TranslateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")
        target = request.data.get("target", "fa")  # default Persian

        if not text:
            return Response(
                {"error": "Text field is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        async def translate():
            async with Translator() as translator:
                return await translator.translate(text, dest=target)

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                translated = asyncio.run(translate())
                return Response(
                    {
                        "original": text,
                        "translated": translated.text,
                        "src_lang": translated.src,
                        "dest_lang": translated.dest,
                    }
                )
            except Exception as e:
                if attempt == max_retries:
                    return Response(
                        {
                            "error": f"Translation failed after {max_retries} attempts: {str(e)}"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )


class LessonsSitemapAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        urls = []

        audio_lessons = (
            Audio.objects.filter(status=PostStatus.ENABLE)
            .only("id", "updated_at")
            .order_by("-updated_at")
        )
        for audio in audio_lessons:
            loc = request.build_absolute_uri(
                reverse("audio-lesson-detail", kwargs={"pk": audio.pk})
            )
            lastmod = audio.updated_at.isoformat() if audio.updated_at else None
            urls.append({"loc": loc, "lastmod": lastmod})

        speaking_lessons = (
            Speaking.objects.filter(status=SpeakingStatus.ENABLE)
            .only("id", "updated_at")
            .order_by("-updated_at")
        )
        for speaking in speaking_lessons:
            loc = request.build_absolute_uri(
                reverse("speaking-lesson-detail", kwargs={"pk": speaking.pk})
            )
            lastmod = speaking.updated_at.isoformat() if speaking.updated_at else None
            urls.append({"loc": loc, "lastmod": lastmod})

        xml = build_sitemap_xml(urls)
        return HttpResponse(xml, content_type="application/xml")
