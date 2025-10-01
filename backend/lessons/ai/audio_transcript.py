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

    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.universal)
    client = aai.Client(api_key=aai.settings.api_key, request_timeout=180)

    transcriber = aai.Transcriber(config=config,http_client=client)
    transcript = transcriber.transcribe(audio_src)
    print('transcript::::::',transcript)
    if transcript.status == "error":
        raise RuntimeError(f"Transcription failed: {transcript.error}")
    
    return transcript.text, transcript.export_subtitles_vtt()




