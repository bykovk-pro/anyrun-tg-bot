import logging
import aiohttp
import validators
from src.lang.director import humanize
from src.lang.decorators import with_locale

@with_locale
async def get_report_by_uuid(api_key: str, uuid: str):
    if not validators.uuid(uuid):
        return {"error": True, "message": await humanize("INVALID_UUID")}

    url = f"https://api.any.run/v1/analysis/{uuid}"
    headers = {
        "Authorization": f"API-Key {api_key}"
    }

    logging.debug(f"Getting report for UUID: {uuid}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {}).get("analysis", {})
                else:
                    error_message = await response.text()
                    logging.error(f"API error: {error_message}")
                    return {"error": True, "message": await humanize("REPORT_ERROR")}
        except Exception as e:
            logging.error(f"Error getting report: {e}")
            return {"error": True, "message": await humanize("ERROR_OCCURRED")}
