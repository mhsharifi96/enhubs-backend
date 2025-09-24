from rest_framework import viewsets
from .models import Audio
from .serializers import AudioSerializer


class AudioLessionViewSet(viewsets.ModelViewSet):
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer


