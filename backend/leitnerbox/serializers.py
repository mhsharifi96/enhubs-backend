from rest_framework import serializers
from leitnerbox.models import Deck, Card, ReviewLog, ReviewQuality

class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'name', 'owner', 'created_at']
        read_only_fields = ['owner', 'created_at']

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id', 'front_text', 'back_text','llm_extractions',
            'interval', 'repetition', 'ease_factor'
        ]
        read_only_fields = [ 'interval', 'repetition', 'ease_factor','llm_extractions']

class ReviewLogSerializer(serializers.ModelSerializer):
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)

    class Meta:
        model = ReviewLog
        fields = ['id', 'card', 'user', 'review_date', 'quality', 'quality_display']
        read_only_fields = ['review_date', 'user', 'quality_display']
