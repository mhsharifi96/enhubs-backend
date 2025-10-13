from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Deck(models.Model):
    """Represents a collection of flashcards (a Leitner box)."""
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Card(models.Model):
    """Represents a single flashcard in a deck."""
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_cards')
    front_text = models.CharField(max_length=500)  # Question or English word
    back_text = models.CharField(max_length=600,null=True,blank=True)  # Answer or meaning
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    interval = models.IntegerField(default=1)  # Spaced repetition interval in days
    repetition = models.IntegerField(default=0)  # Number of successful reviews
    ease_factor = models.FloatField(default=2.5)  # Learning factor for Leitner algorithm

    def __str__(self):
        return self.front_text

class ReviewQuality(models.IntegerChoices):
    """Enumeration for review quality ratings."""
    FORGOT = 0, 'Forgot'
    HARD = 1, 'Hard'
    GOOD = 2, 'Good'
    EASY = 3, 'Easy'

class ReviewLog(models.Model):
    """Stores the review history of a flashcard."""
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_date = models.DateTimeField(default=timezone.now)
    quality = models.IntegerField(choices=ReviewQuality.choices, default=ReviewQuality.GOOD)

    def __str__(self):
        return f"{self.card.front_text} - {self.get_quality_display()}"
