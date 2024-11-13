import logging
import aiohttp
from src.lang.director import humanize
from src.lang.decorators import with_locale

@with_locale
async def get_user_limits(api_key: str):
    url = "https://api.any.run/v1/user"
    headers = {
        "Authorization": f"API-Key {api_key}"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    limits = data.get('data', {}).get('limits', {}).get('api', {})
                    return {
                        "month": limits.get('month', -1),
                        "day": limits.get('day', -1),
                        "hour": limits.get('hour', -1),
                        "minute": limits.get('minute', -1)
                    }
                else:
                    error_message = await response.text()
                    logging.error(f"API error: {error_message}")
                    return {"error": await humanize("API_LIMITS_EXCEEDED")}
        except Exception as e:
            logging.error(f"Error getting user limits: {e}")
            return {"error": await humanize("ERROR_OCCURRED")}
