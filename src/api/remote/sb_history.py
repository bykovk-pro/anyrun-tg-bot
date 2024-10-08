import logging
import aiohttp
from src.lang.director import humanize  # Импортируем humanize для получения текстов

async def get_analysis_history(api_key: str, limit: int = 10, skip: int = 0):
    url = "https://api.any.run/v1/analysis/"
    headers = {
        "Authorization": f"API-Key {api_key}"
    }
    params = {
        "limit": limit,
        "skip": skip
    }

    logging.debug(f"Fetching analysis history with params: limit={limit}, skip={skip}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                logging.debug(f"Received response with status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    logging.debug(f"Data received: {data}")
                    return data.get('data', {}).get('tasks', [])
                else:
                    error_message = await response.json()
                    logging.error(f"Error response: {error_message}")
                    return {"error": error_message.get("message", humanize("UNKNOWN_ERROR"))}
        except Exception as e:
            logging.error(f"Error fetching analysis history: {str(e)}")
            return {"error": str(e)}
