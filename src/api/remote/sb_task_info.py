from enum import Enum
from datetime import datetime
import logging
from src.api.menu_utils import escape_markdown
from dateutil import parser

class ResultType(Enum):
    TEXT = "text"
    IMAGE = "image"

def process_task_info(verdict, date, main_object, uuid, tags, result_type: ResultType):
    if result_type == ResultType.IMAGE:
        return None
    elif result_type == ResultType.TEXT:
        return process_task_info_text(verdict, date, main_object, uuid, tags)
    else:
        logging.error(f"Unknown result type: {result_type}")
        return None

def process_task_info_text(verdict, date, main_object, uuid, tags):
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
        formatted_date = "Unknown date"

    escaped_main_object = escape_markdown(str(main_object))
    escaped_uuid = escape_markdown(str(uuid))

    if tags:
        escaped_tags = ", ".join(f"[{escape_markdown(tag)}]" for tag in tags)
        tags_string = f"🏷️\u00A0{escaped_tags}"
    else:
        tags_string = ""

    result = (
        f"{verdict_icon}\u00A0***{formatted_date}***\n"
        f"📄\u00A0`{escaped_main_object}`\n"
        f"🆔\u00A0`{escaped_uuid}`\n"
        f"{tags_string}"
    )

    return result.strip()
