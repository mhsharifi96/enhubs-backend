from django.urls import path, include
from rest_framework.routers import DefaultRouter
from leitnerbox.views import DeckViewSet, CardViewSet, ReviewLogViewSet

router = DefaultRouter()
router.register(r'decks', DeckViewSet, basename='deck')
router.register(r'cards', CardViewSet, basename='card')
# router.register(r'reviews', ReviewLogViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
