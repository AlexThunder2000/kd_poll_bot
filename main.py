import os
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove, WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)
from datetime import datetime

TOKEN = os.environ["TOKEN"]

UKRAINIAN_WEEKDAYS = {
    "Monday": "понеділок",
    "Tuesday": "вівторок",
    "Wednesday": "середа",
    "Thursday": "четвер",
    "Friday": "п’ятниця",
    "Saturday": "субота",
    "Sunday": "неділя"
}

waiting_for_date = {}

async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Сьогодні", callback_data="poll_today")],
        [InlineKeyboardButton("Ввести іншу дату", callback_data="poll_custom")]
    ]

    # додати WebApp тільки в особистому чаті
    if update.message.chat.type == "private":
        keyboard.append([
            InlineKeyboardButton("Обрати дату в календарі",
                                 web_app=WebAppInfo(url="https://calendar-picker-demo.netlify.app"))
        ])

    await update.message.reply_text(
        "Оберіть дату для опитування:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "poll_today":
        await send_both_polls(update, context, datetime.now())
    elif query.data == "poll_custom":
        user_id = query.from_user.id
        waiting_for_date[user_id] = query.message.chat_id
        await query.message.reply_text("Введіть дату у форматі дд.мм:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = waiting_for_date.get(user_id)

    if not chat_id:
        return

    try:
        parsed_date = datetime.strptime(update.message.text.strip(), "%d.%m")
        parsed_date = parsed_date.replace(year=datetime.now().year)
    except ValueError:
        await update.message.reply_text("Невірний формат дати. Введіть у форматі дд.мм, напр. 03.05")
        return

    del waiting_for_date[user_id]
    await send_both_polls(update, context, parsed_date)

async def send_both_polls(update: Update, context: ContextTypes.DEFAULT_TYPE, date_obj: datetime):
    date_str = date_obj.strftime("%d.%m")
    weekday_en = date_obj.strftime("%A")
    weekday_uk = UKRAINIAN_WEEKDAYS.get(weekday_en, weekday_en)

    question_1 = f"О котрій планую бути? {date_str} ({weekday_uk})"
    options_1 = ["9:00", "10:00", "11:00", "12:00", "16:00", "17:00", "18:00", "19:00", "20:00"]

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question_1,
        options=options_1,
        is_anonymous=False,
        allows_multiple_answers=False
    )

    question_2 = "-"
    options_2 = [
        "Сьогодні не буду, можна перенос?",
        "Сьогодні не буду"
    ]

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question_2,
        options=options_2,
        is_anonymous=False,
        allows_multiple_answers=False
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("poll", poll))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
