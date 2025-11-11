
import re
from urllib.parse import urlparse

def extract_url_and_filename(text: str):
    """
    Extracts the first URL and its file name from a given text.

    Args:
        text (str): Input text containing a URL.

    Returns:
        dict: A dictionary with 'url' and 'file_name' keys (or None if not found).
    """
    match = re.search(r'https?://\S+', text)
    if not match:
        return {"url": None, "title": None}

    url = match.group(0)
    path = urlparse(url).path
    file_name = path.split('/')[-1] if path else None
    if file_name:
        title = file_name.replace('_', ' ').rsplit('.', 1)[0]

        return {"url": url, "title": title}
    
    return {"url": url, "title": file_name}


def convert_vtt_to_json(vtt_text: str):
    # Normalize newlines
    vtt_text = vtt_text.replace('\r\n', '\n').replace('\r', '\n')

    # Ignore header if present
    vtt_text = re.sub(r'^WEBVTT.*?\n+', '', vtt_text, flags=re.S)

    # More tolerant regex for caption blocks
    pattern = re.compile(
        r'(\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}\.\d{3})\s*\n(.*?)(?=\n{2,}|\Z)',
        re.S
    )

    captions = []
    for match in pattern.finditer(vtt_text):
        start, end, text = match.groups()
        captions.append({
            "start": start.strip(),
            "end": end.strip(),
            "text": text.strip().replace('\n', ' '),
            "fa_text": "",
        })

    print(f"Extracted {len(captions)} captions")
    return captions

    