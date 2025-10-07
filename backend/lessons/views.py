from rest_framework import viewsets
from .models import Audio
from .serializers import AudioSerializer

from rest_framework.pagination import PageNumberPagination

class AudioPagination(PageNumberPagination):
    page_size = 4  # number of items per page
    page_size_query_param = 'page_size'  # allow client to set page size
    max_page_size = 50  # maximum page size allowed



class AudioLessionViewSet(viewsets.ModelViewSet):
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer
    pagination_class = AudioPagination