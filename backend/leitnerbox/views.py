from rest_framework import viewsets, permissions, decorators
from rest_framework.decorators import action
from rest_framework.response import Response
from leitnerbox.models import Deck, Card, ReviewLog
from leitnerbox.serializers import DeckSerializer, CardSerializer, ReviewLogSerializer
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class DeckViewSet(viewsets.ModelViewSet):
    """API for managing decks (Leitner boxes)."""
    serializer_class = DeckSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination


    def get_queryset(self):
        return Deck.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @decorators.action(detail=True, methods=['get'], url_path='cards')
    def list_cards(self, request, pk=None):
        """
        List all cards in this deck with pagination.
        GET /api/decks/{id}/cards/
        """
        deck = self.get_object()
        cards = Card.objects.filter(deck=deck)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(cards, request)
        serializer = CardSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class CardViewSet(viewsets.ModelViewSet):
    """API for managing cards."""
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination


    def get_queryset(self):
        return Card.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        # Create a deck if the user doesn't already have one
        deck, _ = Deck.objects.get_or_create(
            owner=user,
            defaults={"name": f"{user.username}'s default deck"}
        )

        serializer.save(owner=user, deck=deck)


class ReviewLogViewSet(viewsets.ModelViewSet):
    """API for logging card reviews."""
    serializer_class = ReviewLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReviewLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
