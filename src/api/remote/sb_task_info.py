from enum import Enum
from datetime import datetime
import logging
from src.api.menu_utils import escape_markdown

class ResultType(Enum):
    TEXT = "text"
    IMAGE = "image"

def process_task_info(verdict, date, main_object, uuid, tags, result_type: ResultType):
    if result_type == ResultType.IMAGE:
        # Пустая функция для обработки изображений
        return None
    elif result_type == ResultType.TEXT:
        return process_task_info_text(verdict, date, main_object, uuid, tags)
    else:
        logging.error(f"Unknown result type: {result_type}")
        return None

def process_task_info_text(verdict, date, main_object, uuid, tags):
    # Обработка verdict
    verdict_icon = {
        "No threats detected": "🔵",
        "Suspicious activity": "🟡",
        "Malicious activity": "🔴",
        0: "🔵",
        1: "🟡",
        2: "🔴"
    }.get(verdict, "⚪")

    # Обработка date
    try:
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        elif isinstance(date, int):
            date = datetime.fromtimestamp(date)
        formatted_date = escape_markdown(date.strftime('%d %B %Y, %H:%M'))
    except Exception as e:
        logging.error(f"Error processing date: {e}")
        formatted_date = "Unknown date"

    # Обработка main_object и uuid
    escaped_main_object = escape_markdown(str(main_object))
    escaped_uuid = escape_markdown(str(uuid))

    # Обработка tags
    if tags:
        escaped_tags = ", ".join(f"[{escape_markdown(tag)}]" for tag in tags)
        tags_string = f"🏷️\u00A0{escaped_tags}"
    else:
        tags_string = ""

    # Формирование итоговой строки
    result = (
        f"{verdict_icon}\u00A0***{formatted_date}***\n"
        f"📄\u00A0`{escaped_main_object}`\n"
        f"🆔\u00A0`{escaped_uuid}`\n"
        f"{tags_string}"
    )

    return result.strip()

