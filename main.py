import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, filters
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

user_threads = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬Напишите свое сообщение и вам ответят в ближайшее время!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if user.id not in user_threads:
        topic = await context.bot.create_forum_topic(
            chat_id=GROUP_ID,
            name=f"{user.first_name or 'User'} ({user.id})"
        )
        user_threads[user.id] = topic.message_thread_id

    thread_id = user_threads[user.id]
    sender = user.username or user.first_name
    text = message.text

    await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=thread_id,
        text=f"📨 Сообщение от @{sender}:\n\n{text}"
    )

    await message.reply_text("✨Сообщение отправлено!\n\nЖдите ответа в ближайшее время.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.start()

    # Автоустановка вебхука при старте
    await app.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")

    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        url_path=BOT_TOKEN,
    )

    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
