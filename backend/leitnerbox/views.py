from rest_framework import viewsets, permissions, decorators
from rest_framework.decorators import action
from rest_framework.response import Response
from leitnerbox.models import Deck, Card, ReviewLog
from leitnerbox.serializers import DeckSerializer, CardSerializer, ReviewLogSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta



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
    
   
    
    @decorators.action(detail=False, methods=['get'], url_path='reviews')
    def reviews(self, request):
        """
        List all cards in this deck with pagination.
        GET /api/decks/reivews/
        """
        cards = Card.objects.filter(
        owner=request.user,
        next_review_at__lte=timezone.now()
        ).order_by('next_review_at')
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(cards, request)
        serializer = CardSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @decorators.action(detail=True, methods=['post'], url_path='reviews')
    def review_card(self, request, pk=None):
        """
        Review a specific card using the SuperMemo2 algorithm.
        POST /api/decks/reviews/<card_id>/
        Body: { "quality": 0–5 }
        """
        card = get_object_or_404(Card, pk=pk, owner=request.user)
        quality = int(request.data.get('quality', -1))

        if quality < 0 or quality > 5:
            return Response(
                {"detail": "Quality must be an integer between 0 and 5."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- SM2 Algorithm ---
        if quality < 3:
            card.repetition = 0
            card.interval = 1
        else:
            if card.repetition == 0:
                card.interval = 1
            elif card.repetition == 1:
                card.interval = 6
            else:
                card.interval = round(card.interval * card.ease_factor)

            card.repetition += 1
            card.ease_factor = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            if card.ease_factor < 1.3:
                card.ease_factor = 1.3

        card.next_review_at = timezone.now() + timedelta(days=card.interval)
        card.save()

        return Response({
            "message": "Card reviewed successfully.",
            "card": {
                "id": card.id,
                "interval": card.interval,
                "repetition": card.repetition,
                "ease_factor": round(card.ease_factor, 2),
            }
        }, status=status.HTTP_200_OK)

    
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

    def retrieve(self, request, *args, **kwargs):
        """Get a single card by ID (only if it belongs to the current user)."""
        try:
            card = self.get_queryset().get(pk=kwargs["pk"])
        except Card.DoesNotExist:
            return Response({"detail": "Card not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(card)
        return Response(serializer.data)


class ReviewLogViewSet(viewsets.ModelViewSet):
    """API for logging card reviews."""
    serializer_class = ReviewLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReviewLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
