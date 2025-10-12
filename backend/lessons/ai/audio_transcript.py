import assemblyai as aai


aai.settings.api_key = "955dcef15e0a47459ab11470d2c5eadb"

def get_transcribe_audio(audio_src: str):
    """
    Transcribes an audio file (local or URL) using AssemblyAI.

    Args:
        audio_file (str): Path to a local audio file or a URL.

    Returns:
        str: Transcribed text.

    Raises:
        RuntimeError: If transcription fails.
    """


    config = aai.TranscriptionConfig(
    # speaker_labels=True,
    format_text=True,
    punctuate=True,
    speech_model=aai.SpeechModel.universal,
    language_detection=True,
    # auto_highlights=True

    )

    transcriber = aai.Transcriber(config=config)
    # transcript = transcriber.transcribe(audio_src)
    transcript = transcriber.submit(audio_src)
    # Wait for the transcription to complete
    transcript.wait_for_completion()

    print('transcript::::::')
    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"Transcription failed: {transcript.error}")
    
    return transcript.text, transcript.export_subtitles_vtt()




