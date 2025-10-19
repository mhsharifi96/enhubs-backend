import os
from django.core.management.base import BaseCommand
from lessons.tasks import create_audio_task  # explicitly import

class Command(BaseCommand):
    help = "Test Celery task"

    def handle(self, *args, **kwargs):
        create_audio_task.delay(
            title="Test",
            file_name="file.m4a",
            uploaded_path_file="/tmp/file.m4a",
            audio_src="Telegram Bot"
        )
        self.stdout.write(self.style.SUCCESS("Task sent to Celery"))