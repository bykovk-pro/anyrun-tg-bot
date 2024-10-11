import logging
import aiohttp
from src.lang.director import humanize

async def run_url_analysis(api_key: str, url: str):
    api_url = "https://api.any.run/v1/analysis"
    headers = {
        "Authorization": f"API-Key {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "obj_type": "url",
        "obj_url": url
    }

    logging.debug(f"Making API request to run URL analysis for: {url}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, headers=headers, json=payload) as response:
                logging.debug(f"Received response with status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_message = await response.json()
                    logging.error(f"Error response: {error_message}")
                    return {"error": error_message.get("message", humanize("UNKNOWN_ERROR"))}
        except Exception as e:
            logging.error(f"Error running URL analysis: {str(e)}")
            return {"error": str(e)}

async def run_file_analysis(api_key: str, file_content: bytes, file_name: str):
    api_url = "https://api.any.run/v1/analysis"
    headers = {
        "Authorization": f"API-Key {api_key}"
    }
    files = {
        'file': (file_name, file_content)
    }
    data = {
        'obj_type': 'file'
    }

    logging.debug(f"Making API request to run file analysis for: {file_name}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, headers=headers, data=data, files=files) as response:
                logging.debug(f"Received response with status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_message = await response.json()
                    logging.error(f"Error response: {error_message}")
                    return {"error": error_message.get("message", humanize("UNKNOWN_ERROR"))}
        except Exception as e:
            logging.error(f"Error running file analysis: {str(e)}")
            return {"error": str(e)}
