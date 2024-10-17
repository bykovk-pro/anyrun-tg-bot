import logging
import aiohttp
from src.lang.director import humanize
from src.api.remote.sb_status import get_analysis_status

async def get_analysis_history(api_key: str, limit: int = 10, skip: int = 0):
    url = "https://api.any.run/v1/analysis/"
    headers = {
        "Authorization": f"API-Key {api_key}"
    }
    params = {
        "limit": limit,
        "skip": skip
    }

    logging.debug(f"Making API request to fetch analysis history with params: limit={limit}, skip={skip}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                logging.debug(f"Received response with status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    tasks = data.get('data', {}).get('tasks', [])
                    return tasks
                elif response.status == 401:
                    return {"error": True, "message": "Wrong authorization data"}
                else:
                    error_message = await response.json()
                    logging.error(f"Error response: {error_message}")
                    return {"error": True, "message": error_message.get("message", humanize("UNKNOWN_ERROR"))}
        except Exception as e:
            logging.error(f"Error fetching analysis history: {str(e)}")
            return {"error": True, "message": str(e)}

#async def get_active_tasks(api_key: str):
#    tasks = await get_analysis_history(api_key, limit=10)  # Вернули лимит на 10 задач
#    if isinstance(tasks, list):
#        active_tasks = []
#        for task in tasks:
#            status = await get_analysis_status(api_key, task['uuid'])
#            if status.get('status') in ['queued', 'running']:
#                task['status'] = status['status']
#                active_tasks.append(task)
#        logging.debug(f"Found {len(active_tasks)} active tasks out of {len(tasks)} total tasks")
#        return active_tasks
#    return tasks
