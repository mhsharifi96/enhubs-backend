import os
import requests
from django.conf import settings

def download_file(url: str, filename: str) -> str:
    """
    Download a file from the given URL and save it under MEDIA_ROOT/audio/.
    Returns the relative file path for storing in the model.
    """
    download_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    os.makedirs(download_dir, exist_ok=True)

    file_path = os.path.join(download_dir, filename)

    response = requests.get(url, stream=True, timeout=500)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # return relative path (to store in FileField/CharField)
    return file_path