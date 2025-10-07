from rest_framework import viewsets, mixins
from .models import Audio, Category, PostStatus
from .serializers import AudioSerializer, CategorySerializer

from rest_framework.pagination import PageNumberPagination

class AudioPagination(PageNumberPagination):
    page_size = 4  # number of items per page
    page_size_query_param = 'page_size'  # allow client to set page size
    max_page_size = 50  # maximum page size allowed



class AudioLessionViewSet(viewsets.ModelViewSet):
    queryset = Audio.objects.all().filter(status=PostStatus.ENABLE).order_by('-created_at')
    serializer_class = AudioSerializer
    pagination_class = AudioPagination


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

