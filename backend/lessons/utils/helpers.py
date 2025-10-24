
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


