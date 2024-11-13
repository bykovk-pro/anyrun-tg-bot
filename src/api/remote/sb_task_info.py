from enum import Enum
import logging
from src.api.menu_utils import escape_markdown
from datetime import datetime
from dateutil import parser
from src.lang.director import humanize
from src.lang.decorators import with_locale

class ResultType(Enum):
    TEXT = "text"

@with_locale
async def process_task_info(verdict, date, main_object, uuid, tags, status, result_type: ResultType):
    if result_type != ResultType.TEXT:
        logging.error(f"Unsupported result type: {result_type}")
        return None

    try:
        logging.debug(f"Processing task info: verdict={verdict}, date={date}, object={main_object}, uuid={uuid}, tags={tags}")

        verdict_icon = {
            "No threats detected": "🔵",
            "Suspicious activity": "🟡",
            "Malicious activity": "🔴",
            0: "🔵",
            1: "🟡",
            2: "🔴"
        }.get(verdict, "⚪")

        try:
            if isinstance(date, str):
                date = parser.isoparse(date)
            elif isinstance(date, int):
                date = datetime.fromtimestamp(date)
            formatted_date = escape_markdown(date.strftime('%d %B %Y, %H:%M'))
        except Exception as e:
            logging.error(f"Error processing date: {e}")
            formatted_date = escape_markdown(await humanize("UNKNOWN_DATE"))

        escaped_main_object = escape_markdown(str(main_object))
        escaped_uuid = escape_markdown(str(uuid))

        tags_string = ""
        if tags:
            escaped_tags = ", ".join(f"[{escape_markdown(tag)}]" for tag in tags)
            tags_string = f"\n🏷️ {escaped_tags}"

        message = (
            f"{verdict_icon} {formatted_date}\n\n"
            f"📄 `{escaped_main_object}`\n\n"
            f"🆔 `{escaped_uuid}`\n\n"
            f"{tags_string}"
        )

        logging.debug(f"Generated message: {message}")
        return message

    except Exception as e:
        logging.error(f"Error in process_task_info: {e}", exc_info=True)
        return None
