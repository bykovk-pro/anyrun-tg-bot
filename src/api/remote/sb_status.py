import logging
import aiohttp
import json
from src.lang.director import humanize

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
                    return {"error": f"HTTP error: {response.status}"}
                
                async for line in response.content:
                    if line.startswith(b'data: '):
                        data = json.loads(line[6:].decode('utf-8'))
                        return process_status_response(data)
                
                # Если мы дошли до этой точки, значит задача завершена
                return {"status": "completed", "message": humanize("ANALYSIS_STATUS_COMPLETED")}
        except Exception as e:
            logging.error(f"Error getting analysis status: {str(e)}")
            return {"error": str(e)}

def process_status_response(data):
    task = data.get('task', {})
    status = task.get('status')
    if status == 100 or task.get('actions', {}).get('manualclosed'):
        return {"status": "completed", "message": humanize("ANALYSIS_STATUS_COMPLETED")}
    elif status == -1:
        return {"status": "failed", "message": humanize("ANALYSIS_STATUS_FAILED")}
    elif status is not None:
        return {"status": "running", "message": humanize("ANALYSIS_STATUS_RUNNING")}
    else:
        return {"status": "unknown", "message": humanize("ANALYSIS_STATUS_UNKNOWN")}
