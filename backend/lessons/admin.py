from django.contrib import admin

# Register your models here.
from .models import Audio , PostStatus
from lessons.tasks import process_audio


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.audio_src and (obj.status != PostStatus.ENABLE or obj.status != PostStatus.DISABLE) :  # only trigger if audio exists and not already ENABLE
            process_audio.delay(obj.id)