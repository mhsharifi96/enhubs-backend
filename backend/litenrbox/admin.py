from django.contrib import admin
from litenrbox.models import Deck, Card, ReviewLog

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('front_text', 'back_text', 'deck', 'owner', 'created_at', 'updated_at')

@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ('card', 'user', 'review_date', 'quality')


# Register your models here.
