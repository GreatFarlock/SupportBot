from telegram import Update, ForumTopic
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import logging

# 🔧 Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = "7664167305:AAEyiGvr-cC9lEmKz2MQ12wu-QQEU5J75X8"
GROUP_ID = -1002471723895

user_threads = {}

async def pre_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "/start":
        await update.message.reply_text(
            "❗️Добро пожаловать в бота поддержки!\n\n"
            "💬Через него вы можете связаться с командой VineSoft и модерацией чата!"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬Напишите свое сообщение и вам ответят в ближайшее время!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if user.id not in user_threads:
        topic: ForumTopic = await context.bot.create_forum_topic(
            chat_id=GROUP_ID,
            name=f"{user.first_name or 'User'} ({user.id})"
        )
        user_threads[user.id] = topic.message_thread_id

    thread_id = user_threads[user.id]

    await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=thread_id,
        text=f"📨 Сообщение от @{user.username or user.first_name}:\n\n{message.text}"
    )

    await message.reply_text("✨Сообщение отправлено!\n\nЖдите ответа в ближайшее время.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, pre_start_message), group=0)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message), group=1)

    app.run_polling()

if __name__ == "__main__":
    main()
