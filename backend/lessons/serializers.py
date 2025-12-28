from rest_framework import serializers
from .models import Audio, Category, tag , Speaking, SpeakingAnswer
import json


class CategorySerializer(serializers.ModelSerializer):

    class Meta: 
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = tag
        fields = ['name', 'slug']

class AudioSerializer(serializers.ModelSerializer):
    notes = serializers.JSONField(required=False, allow_null=True)
    vocabulary_items = serializers.JSONField(required=False, allow_null=True)
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Audio
        fields = [
            "id",
            "title",
            "category",
            "audio_src",
            "uploaded_url",
            "transcript",
            "raw_transcript",
            "transcript_json",
            "notes",
            "vocabulary_items",
        ]
    

    def to_representation(self, instance):
        """Convert DB string -> JSON object"""
        rep = super().to_representation(instance)
        for field in ["notes", "vocabulary_items"]:
            value = getattr(instance, field)
            if value:
                try:
                    rep[field] = json.loads(value)
                except Exception:
                    rep[field] = value  # fallback if not valid JSON
        
        rep['vocabulary'] = rep.pop('vocabulary_items', None)
        return rep

class SpeakingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingAnswer
        fields = [
            "answer_text",
            "translate_text",
            "audio_url",
            "created_at",
        ]


class SpeakingDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    answers = SpeakingAnswerSerializer(many=True, read_only=True)
    class Meta: 
        model= Speaking
        fields = [
            "id",
            "slug",
            "title",
            "question",
            "text",
            "category",
            "answers",
            "tags"

        ]


class SpeakingListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta: 
        model= Speaking
        fields = [
            "id",
            "slug",
            "title",
            "question",
            "category",
            "tags"

        ]
    