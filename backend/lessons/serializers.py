from rest_framework import serializers
from .models import Audio
import json



class AudioSerializer(serializers.ModelSerializer):
    notes = serializers.JSONField(required=False, allow_null=True)
    vocabulary_items = serializers.JSONField(required=False, allow_null=True)

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
