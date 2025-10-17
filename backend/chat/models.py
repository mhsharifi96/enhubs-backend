import uuid
from django.db import models
from django.contrib.auth.models import User

class ConversationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # random unique ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    history = models.JSONField(default=list)  # [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"