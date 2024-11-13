import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.lang.director import humanize
from src.api.remote.sb_task_info import process_task_info, ResultType
from src.lang.decorators import with_locale, localized_message

@with_locale
async def display_report_info(update: Update, context: ContextTypes.DEFAULT_TYPE, report):
    try:
        main_object = report.get("content", {}).get("mainObject", {})
        name = main_object.get("filename") if main_object.get("type") == "file" else main_object.get("url", await humanize("UNKNOWN_OBJECT"))
        verdict = report.get("scores", {}).get("verdict", {}).get("threatLevelText", await humanize("UNKNOWN_VERDICT"))
        date = report.get("creationText", "")
        uuid = report.get("uuid", await humanize("UNKNOWN_UUID"))
        tags = [tag['tag'] for tag in report.get("tags", []) if 'tag' in tag]
        status = "completed"

        logging.debug(f"Processing report data: name={name}, verdict={verdict}, date={date}, uuid={uuid}, tags={tags}")

        text_message = await process_task_info(verdict, date, name, uuid, tags, status, ResultType.TEXT)
        if not text_message:
            logging.error("Failed to generate text message from task info")
            await localized_message("ERROR_PROCESSING_REPORT")(update)
            return

        try:
            await update.message.reply_text(text_message, parse_mode='MarkdownV2')
        except Exception as e:
            logging.error(f"Error sending formatted message: {e}")
            await update.message.reply_text(text_message)

        keyboard = [[
            InlineKeyboardButton(
                await humanize("VIEW_REPORT_ONLINE"), 
                url=f"https://app.any.run/tasks/{uuid}/"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            await humanize("VIEW_FULL_REPORT"),
            reply_markup=reply_markup
        )

    except Exception as e:
        logging.error(f"Error displaying report: {e}", exc_info=True)
        await localized_message("ERROR_DISPLAYING_REPORT")(update)
