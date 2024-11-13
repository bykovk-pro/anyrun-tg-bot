import logging
import aiohttp
import json
from src.lang.director import humanize
from src.lang.decorators import with_locale

@with_locale
async def get_analysis_status(api_key: str, task_id: str):
    api_url = f"https://api.any.run/v1/analysis/status/{task_id}"
    headers = {
        "Authorization": f"API-Key {api_key}",
        "Accept": "text/event-stream"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    return {"error": await humanize("STATUS_CHECK_ERROR")}
                
                async for line in response.content:
                    if line.startswith(b'data: '):
                        data = json.loads(line[6:].decode('utf-8'))
                        return await process_status_response(data)
                
                return {"status": "completed", "message": await humanize("ANALYSIS_COMPLETED")}
        except Exception as e:
            logging.error(f"Error getting analysis status: {e}")
            return {"error": await humanize("ERROR_OCCURRED")}

@with_locale
async def process_status_response(data):
    task = data.get('task', {})
    status = task.get('status')
    
    if status == 100 or task.get('actions', {}).get('manualclosed'):
        return {"status": "completed", "message": await humanize("ANALYSIS_COMPLETED")}
    elif status == -1:
        return {"status": "failed", "message": await humanize("ANALYSIS_FAILED")}
    else:
        return {"status": "running", "message": await humanize("ANALYSIS_STATUS_RUNNING")}
