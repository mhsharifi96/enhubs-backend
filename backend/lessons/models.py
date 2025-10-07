from django.db import models


class PostStatus(models.TextChoices):
    INIT = "init", "Init"
    DOWNLOAD = "download", "Download"
    UPLOAD = "upload", "Upload to Ceph"
    TRANSCRIBE = "transcribe", "Transcribe"
    FORMAT_TEXT = "format_text", "Format text"
    EXTRACT_NOTE = "is_extract_note", "Extract note"
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
    notes = models.TextField(null=True, blank=True)
    vocabulary_items =  models.TextField(null=True, blank=True)


    # Many-to-Many: avoid repeating vocab

    def __str__(self):
        return self.title



