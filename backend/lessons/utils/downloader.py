import os
import requests
from django.conf import settings
from requests.exceptions import RequestException


def download_file_deprecated(url: str, filename: str) -> str:
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



def download_file(url: str, filename: str) -> str:
    """
    Download a file from the given URL with a retry mechanism.

    It first tries to download directly (no proxy). 
    If it fails, it tries two more times using the SOCKS5 proxy defined in settings.
    
    Returns the relative file path for storing in the model.
    """
    download_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    os.makedirs(download_dir, exist_ok=True)

    file_path = os.path.join(download_dir, filename)
    
    # Safely get the custom proxy URL from Django settings
    proxy_url = getattr(settings, 'PROXY_SOCKS5_URL', None)

    # Define the proxy configuration dictionary for the proxied attempts
    proxy_config = None
    if proxy_url:
        proxy_config = {
            "http": proxy_url,
            "https": proxy_url,
        }
    
    # Define the sequence of attempts: (proxies, attempt_number, method_name)
    attempts = [
        (None, 1, "Direct"),                  # First attempt: No proxy
        (proxy_config, 2, "Proxy (Attempt 1)"), # Second attempt: With proxy
        (proxy_config, 3, "Proxy (Attempt 2)"), # Third attempt: With proxy
    ]

    for proxies, attempt_num, method in attempts:
        if proxies is None or proxy_url:
            print(f"Attempt {attempt_num}: Downloading via {method}...")
        elif attempt_num > 1:
            print(f"Attempt {attempt_num}: Skipping proxy try, PROXY_SOCKS5_URL not configured.")
            continue # Skip proxy attempts if the setting is missing

        try:
            response = requests.get(
                url, 
                stream=True, 
                timeout=500,
                proxies=proxies # Pass the proxy configuration
            )
            response.raise_for_status() # Raise HTTPError for bad status codes (4xx or 5xx)

            # --- SUCCESS ---
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Download succeeded on attempt {attempt_num}.")
            return file_path

        except RequestException as e:
            print(f"Attempt {attempt_num} failed: {e.__class__.__name__} - {e}")
            if attempt_num == len(attempts):
                # All attempts failed, re-raise the last exception
                raise

    # Fallback to catch unhandled errors, although the loop should cover it
    raise RequestException("File download failed after all attempts.")