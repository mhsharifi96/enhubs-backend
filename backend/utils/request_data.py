import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseRequest():

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def aget(self, url: str, params: dict | None = None, headers: dict | None = None) -> dict:
        """Send an asynchronous GET request."""
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                try:
                    return await response.json()
                except aiohttp.ClientResponseError as e:
                    logger.error(f"Error: {e.status} - {e.message}")
                    raise
                except Exception as e:
                    logger.error(f"Error: {e}")
                    raise

    async def apost(self, url: str, data: dict | None = None, headers: dict | None = None) -> dict:
        """Send an asynchronous POST request."""
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(url, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                try:
                    return await response.json()
                except aiohttp.ClientResponseError as e:
                    logger.error(f"Error: {e.status} - {e.message}")
                    raise
                except Exception as e:
                    logger.error(f"Error: {e}")
                    raise




# if __name__ == "__main__":
#     asyncio.run(get_jwt_token("admin", "F@temeh110"))