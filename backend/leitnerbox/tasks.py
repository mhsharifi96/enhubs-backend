
from celery import shared_task
from leitnerbox.models import Card
from lessons.ai.llm import extract_keywords_or_idioms

@shared_task
def extract_llm_keywords_for_card(card_id):
    try:
        card = Card.objects.get(id=card_id)
        sentence = card.front_text
        status, extractions = extract_keywords_or_idioms(sentence)
        if status:
            card.llm_extractions = extractions
            card.save()
    except Exception as e:
        print(f"Error extracting keywords for Card ID {card_id}: {str(e)}")