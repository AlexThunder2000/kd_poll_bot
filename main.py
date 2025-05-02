import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
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

async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        input_date = context.args[0]
        try:
            parsed_date = datetime.strptime(input_date, "%d.%m")
            parsed_date = parsed_date.replace(year=datetime.now().year)
        except ValueError:
            await update.message.reply_text("Невірний формат дати. Використовуйте формат дд.мм")
            return
    else:
        parsed_date = datetime.now()

    date_str = parsed_date.strftime("%d.%m")
    weekday_en = parsed_date.strftime("%A")
    weekday_uk = UKRAINIAN_WEEKDAYS.get(weekday_en, weekday_en)

    question = f"О котрій планую бути? {date_str} ({weekday_uk})"
    options = ["9:00", "10:00", "11:00", "12:00", "16:00", "17:00", "18:00", "19:00", "20:00"]

    await update.message.chat.send_poll(
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("poll", poll))
app.run_polling()
