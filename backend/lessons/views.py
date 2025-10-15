from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from rest_framework import viewsets, mixins
from .models import Audio, Category, PostStatus
from .serializers import AudioSerializer, CategorySerializer

from rest_framework.pagination import PageNumberPagination
from googletrans import Translator

import asyncio




class AudioPagination(PageNumberPagination):
    page_size = 10  # number of items per page
    page_size_query_param = 'page_size'  # allow client to set page size
    max_page_size = 10  # maximum page size allowed



class AudioLessionViewSet(viewsets.ModelViewSet):
    serializer_class = AudioSerializer
    pagination_class = AudioPagination

    def get_queryset(self):
        queryset = Audio.objects.filter(status=PostStatus.ENABLE).order_by('-created_at')

        category_name = self.request.query_params.get('category')

        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        return queryset


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"


class TranslateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")
        target = request.data.get("target", "fa")  # default Persian

        if not text:
            return Response({"error": "Text field is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        async def translate():
            async with Translator() as translator:
                return await translator.translate(text, dest=target)

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                translated = asyncio.run(translate())
                return Response({
                    "original": text,
                    "translated": translated.text,
                    "src_lang": translated.src,
                    "dest_lang": translated.dest,
                })
            except Exception as e:
                if attempt == max_retries:
                    return Response(
                        {"error": f"Translation failed after {max_retries} attempts: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )