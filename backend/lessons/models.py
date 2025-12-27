from django.db import models
from django.contrib.auth.models import User


class PostStatus(models.TextChoices):
    INIT = "init", "Init"
    DOWNLOAD = "download", "Download"
    UPLOAD = "upload", "Upload to Ceph"
    TRANSCRIBE = "transcribe", "Transcribe"
    FORMAT_TEXT = "format_text", "Format text"
    EXTRACT_NOTE = "is_extract_note", "Extract note"
    TRANSLATE_TEXT = "translate_text", "Translate text"
    ENABLE = "enbale", "Enable"
    DISABLE = "disable", "Disable"


class SpeakingStatus(models.TextChoices):
    INIT = "init", "Init"
    GENERATE_TEXT = "GENERATE_TEXT", "GENERATE TEXT"
    ENABLE = "enbale", "Enable"
    DISABLE = "disable", "Disable"

class Language(models.TextChoices):
    ENGLISH = "ENGLISH", "english"
    GERMAN = "GERMAN", "german"


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    def __str__(self):
        return self.name

class tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    def __str__(self):
        return self.name




class Audio(models.Model):

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=PostStatus.choices, 
                            default=PostStatus.INIT)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
    audio_src = models.URLField(blank=True,null=True)
    local_file = models.CharField(max_length=255, blank=True,null=True)
    uploaded_url = models.URLField(blank=True,null=True)
    raw_transcript = models.TextField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    transcript_json = models.JSONField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    vocabulary_items =  models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(tag, blank=True)
    language = models.CharField(max_length=30, choices=Language.choices , default=Language.ENGLISH)
    created_at = models.DateTimeField(auto_now_add=True)  # automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)      # automatically updated on save


    # Many-to-Many: avoid repeating vocab

    def __str__(self):
        return self.title
    


class AudioHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_history')
    audio = models.ForeignKey('Audio', on_delete=models.CASCADE, related_name='views')
    views_count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'audio')  # one record per user-audio pair

    def __str__(self):
        return f"{self.user.username} listened to {self.audio.title} ({self.views_count} times)"




class Speaking(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    question = models.TextField(null=True,blank=True)
    text = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=30, choices=Language.choices , default=Language.ENGLISH)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
    tags = models.ManyToManyField(tag, blank=True)
    status = models.CharField(max_length=20, choices=SpeakingStatus.choices, 
                            default=PostStatus.INIT)
    created_at = models.DateTimeField(auto_now_add=True)  # automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)      # automatically updated on save

    def __str__(self):
        return self.title

class SpeakingAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speaking_answers')
    speaking = models.ForeignKey('Speaking', on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(null=True, blank=True)
    translate_text = models.TextField(null=True, blank=True)
    audio_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s answer to {self.speaking.title}"