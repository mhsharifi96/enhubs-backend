import time
import random
from celery import shared_task
from lessons.ai.audio_transcript import get_transcribe_audio
from lessons.ai.llm import llm_clean_text, extract_important_notes, translate_text
from lessons.utils.downloader import download_file
from lessons.utils.s3 import upload_file
from lessons.utils.helpers import convert_vtt_to_json

import json

from lessons.models import Audio, PostStatus

# Define the step order
STEP_ORDER = [
    PostStatus.INIT,
    PostStatus.DOWNLOAD,
    PostStatus.UPLOAD,
    PostStatus.TRANSCRIBE,
    PostStatus.FORMAT_TEXT,
    PostStatus.EXTRACT_NOTE,
    PostStatus.TRANSLATE_TEXT,
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
    if not audio.raw_transcript:
        audio.raw_transcript, audio.transcript = get_transcribe_audio(
            audio.uploaded_url
        )
        audio.transcript_json = convert_vtt_to_json(audio.transcript)
    else:
        vtt_dict =  convert_vtt_to_json(audio.transcript)
        audio.transcript_json = vtt_dict

    audio.status = PostStatus.TRANSCRIBE
    audio.save()


def format_audio_text(audio: Audio):
    if audio.raw_transcript:
        audio.raw_transcript = llm_clean_text(audio.raw_transcript)
    audio.status = PostStatus.FORMAT_TEXT
    audio.save()


def extract_audio_notes(audio: Audio):
    # Save extracted notes if needed
    note = extract_important_notes(audio.transcript)
    try:
        note_json = json.loads(note)
        audio.notes = json.dumps(note_json.get("grammar", ""))
        audio.vocabulary_items = json.dumps(note_json.get("vocabulary", []))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    finally:
        audio.status = PostStatus.EXTRACT_NOTE
        audio.save()


def translate_audio_text(audio: Audio):
    CHUNK_SIZE = 30
    OVERLAP = 5  # number of overlapping items between chunks

    if audio.transcript_json:
        translated_transcript = []
        transcript = audio.transcript_json
        transcript_length = len(transcript)

        # Step through with overlap
        for i in range(0, transcript_length, CHUNK_SIZE - OVERLAP):
            print(f"Translating chunk {i} of {transcript_length}")
            chunk = transcript[i : i + CHUNK_SIZE]

            # translate current chunk
            translated_chunk = translate_text(chunk)

            # avoid duplicate overlap items except for the first chunk
            if i > 0:
                translated_chunk = translated_chunk[OVERLAP:]

            translated_transcript.extend(translated_chunk)

            # stop if we've reached or passed the end
            if i + CHUNK_SIZE >= transcript_length:
                break

        audio.transcript_json = translated_transcript
    
    audio.status = PostStatus.TRANSLATE_TEXT
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
    PostStatus.TRANSLATE_TEXT: translate_audio_text,
    PostStatus.ENABLE: enable_audio,
}


@shared_task
def process_audio(audio_id: int):
    """
    Process an audio from its current step through all remaining steps until ENABLE.
    Each step is only executed once and retried up to 3 times if it fails.
    """
    try:
        rand_int = random.randint(1, 10)
        time.sleep(rand_int)
        audio = Audio.objects.get(id=audio_id)
        print(f"start process after {rand_int}s for audio with id {audio_id}")

        current_index = STEP_ORDER.index(audio.status)

        # Loop through current and all next steps
        for status in STEP_ORDER[current_index:]:
            action = STEP_ACTIONS.get(status)
            if not action:
                continue

            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    print(
                        f"Audio {audio_id}: running step '{status}' (attempt {attempt}/{max_retries})"
                    )
                    action(audio)
                    print(f"Audio {audio_id}: completed step '{status}'")
                    break  # success → move to next step
                except Exception as e:
                    print(
                        f"Audio {audio_id}: step '{status}' failed on attempt {attempt}: {e}"
                    )
                    if attempt < max_retries:
                        print("Retrying in 2 seconds...")
                        time.sleep(2)
                    else:
                        print(
                            f"Audio {audio_id}: step '{status}' failed after {max_retries} attempts."
                        )
                        raise  # stop processing further steps

    except Audio.DoesNotExist:
        print(f"Audio with ID {audio_id} not found.")


@shared_task
def create_audio_task(
    title: str, file_name: str, uploaded_path_file: str, audio_src: str
):
    status: str = PostStatus.UPLOAD
    audio = Audio.objects.create(
        title=title or file_name,
        uploaded_url=uploaded_path_file,
        audio_src=audio_src,
        status=status,
    )
    process_audio.delay(audio.id)
    print(f"Audio {audio.id} created and processing task triggered.")
