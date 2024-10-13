import logging
import aiohttp
from src.lang.director import humanize
import validators

async def get_report_by_uuid(api_key: str, uuid: str):
    if not validators.uuid(uuid):
        return {"error": True, "message": humanize("INVALID_UUID")}

    url = f"https://api.any.run/v1/analysis/{uuid}"
    headers = {
        "Authorization": f"API-Key {api_key}"
    }

    logging.debug(f"Making API request to fetch report for UUID: {uuid}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                logging.debug(f"Received response with status: {response.status}")
                response_text = await response.text()
                logging.debug(f"Response content: {response_text[:200]}...")    
                if response.status == 200:
                    data = await response.json()
                    analysis = data.get("data", {}).get("analysis", {})
                    logging.debug(f"Analysis of the report (truncated): {str(analysis)[:200]}")
                    return analysis
                else:
                    error_message = await response.json()
                    logging.error(f"Error response: {error_message}")
                    return {"error": error_message.get("message", humanize("UNKNOWN_ERROR"))}
        except Exception as e:
            logging.error(f"Error fetching report: {str(e)}")
            return {"error": str(e)}
