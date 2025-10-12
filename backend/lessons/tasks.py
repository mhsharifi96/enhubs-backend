
from celery import shared_task
from lessons.ai.audio_transcript import get_transcribe_audio
from lessons.ai.llm import llm_clean_text , extract_important_notes
from lessons.utils.downloader import download_file
from lessons.utils.s3 import upload_file

import json

from lessons.models import Audio , PostStatus

# Define the step order
STEP_ORDER = [
    PostStatus.INIT,
    PostStatus.DOWNLOAD,
    PostStatus.UPLOAD,
    PostStatus.TRANSCRIBE,
    PostStatus.FORMAT_TEXT,
    PostStatus.EXTRACT_NOTE,
    PostStatus.ENABLE,
]


def download_and_upload_audio(audio: Audio):
    """
    Handles INIT, DOWNLOAD, and UPLOAD statuses:
      - INIT: download then upload
      - DOWNLOAD: upload only
      - UPLOAD: skip (already done)
    """
    try:
        if audio.status == PostStatus.INIT:
            # Step 1: Download
            local_path = download_file(audio.audio_src, f"audio_{audio.id}.mp3")
            audio.local_file = local_path
            audio.status = PostStatus.DOWNLOAD
            audio.save()
            print(f"Audio {audio.id}: downloaded -> {local_path}")

            # Step 2: Upload
            uploaded_url = upload_file(local_path)
            audio.uploaded_url = uploaded_url
            audio.status = PostStatus.UPLOAD
            audio.save()
            print(f"Audio {audio.id}: uploaded -> {uploaded_url}")

        elif audio.status == PostStatus.DOWNLOAD:
            # Already downloaded → just upload
            local_path = audio.local_file
            uploaded_url = upload_file(local_path)
            audio.uploaded_url = uploaded_url
            audio.status = PostStatus.UPLOAD
            audio.save()
            print(f"Audio {audio.id}: uploaded -> {uploaded_url}")

        elif audio.status == PostStatus.UPLOAD:
            print(f"Audio {audio.id}: already uploaded, skipping.")

    except Exception as e:
        print(f"Error in download_and_upload_audio for audio {audio.id}: {e}")
        raise



def transcribe_audio(audio: Audio):

    if not audio.raw_transcript and audio.audio_src:
        audio.raw_transcript , audio.transcript = get_transcribe_audio(audio.uploaded_url)
    audio.status = PostStatus.TRANSCRIBE
    audio.save()

def format_audio_text(audio: Audio):
    if not audio.transcript and audio.raw_transcript:
        audio.raw_transcript = llm_clean_text(audio.raw_transcript)
    audio.status = PostStatus.FORMAT_TEXT
    audio.save()

def extract_audio_notes(audio: Audio):
    # Save extracted notes if needed
    note= extract_important_notes(audio.transcript)
    try:
        note_json = json.loads(note)
        audio.notes = json.dumps(note_json.get("grammar", ""))
        audio.vocabulary_items = json.dumps(note_json.get("vocabulary", []))
        audio.status = PostStatus.EXTRACT_NOTE
    except json.JSONDecodeError as e:
        audio.status = PostStatus.EXTRACT_NOTE
        print(f"Error decoding JSON: {e}")
   
    finally:
        audio.save()

def enable_audio(audio: Audio):

    audio.status = PostStatus.ENABLE
    audio.save()


STEP_ACTIONS = {
    PostStatus.INIT: download_and_upload_audio,
    PostStatus.DOWNLOAD: download_and_upload_audio,
    PostStatus.UPLOAD: download_and_upload_audio,
    PostStatus.TRANSCRIBE: transcribe_audio,
    PostStatus.FORMAT_TEXT: format_audio_text,
    PostStatus.EXTRACT_NOTE: extract_audio_notes,
    PostStatus.ENABLE: enable_audio,
}


@shared_task
def process_audio(audio_id: int):
    """
    Process a audio from its current step through all remaining steps until ENABLE.
    Each step is only executed once.
    """
    try:
        audio = Audio.objects.get(id=audio_id)
        current_index = STEP_ORDER.index(audio.status)

        # Loop through current and all next steps
        for status in STEP_ORDER[current_index:]:
            action = STEP_ACTIONS.get(status)
            if action:
                action(audio)
                print(f"Audio {audio_id}: completed step '{status}'")

    except Audio.DoesNotExist:
        print(f"Audio with ID {audio_id} not found.")
    # except Exception as e:
    #     print(f"Error processing audio {audio_id}: {e}")
    #     raise e
