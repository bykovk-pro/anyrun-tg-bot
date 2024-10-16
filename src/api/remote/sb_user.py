import logging
import aiohttp
from src.api.security import check_user_groups, check_user_api_keys, rate_limiter
from src.lang.director import humanize

async def get_api_limits(bot, user_id, required_group_ids):
    if not await check_user_groups(bot, user_id, required_group_ids):
        return "You are not in the required groups."

    if not await check_user_api_keys(user_id):
        return "You do not have any active API keys."

    if not await rate_limiter(user_id):
        return "Rate limit exceeded. Please wait before making another request."

    return "API limits retrieved successfully."

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
                    month = limits.get('month', -1)
                    day = limits.get('day', -1)
                    hour = limits.get('hour', -1)
                    minute = limits.get('minute', -1)

                    return (
                        f"{humanize('YOUR_SANDBOX_API_LIMITS')}:\n"
                        f"{humanize('MONTH')} - {'Unlimited' if month == -1 else month}\n"
                        f"{humanize('DAY')} - {'Unlimited' if day == -1 else day}\n"
                        f"{humanize('HOUR')} - {'Unlimited' if hour == -1 else hour}\n"
                        f"{humanize('MINUTE')} - {'Unlimited' if minute == -1 else minute}"
                    )
                else:
                    try:
                        error_message = await response.json()
                    except ValueError:
                        error_message = {"message": "Response is not valid JSON"}
                    return {"error": error_message.get("message", humanize("UNKNOWN_ERROR"))}
        except Exception as e:
            logging.error(f"Error fetching user limits: {str(e)}")
            return {"error": str(e)}
