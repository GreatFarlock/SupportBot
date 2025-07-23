import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from http import HTTPStatus
from telegram import Update, ForumTopic
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

logging.basicConfig(level=logging.INFO)

app_ptb = (
    Application.builder()
    .token(BOT_TOKEN)
    .updater(None)
    .build()
)

user_threads = {}

async def pre_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "/start":
        await update.message.reply_text(
            "❗️Добро пожаловать в бота поддержки!\n\n"
            "💬Через него вы можете связаться с командой VineSoft и модерацией чата!"
        )

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬Напишите свое сообщение и вам ответят в ближайшее время!")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if user.id not in user_threads:
        topic = await context.bot.create_forum_topic(
            chat_id=GROUP_ID,
            name=f"{user.first_name or 'User'} ({user.id})"
        )
        user_threads[user.id] = topic.message_thread_id

    thread = user_threads[user.id]
    await context.bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=thread,
        text=f"📨 Сообщение от @{user.username or user.first_name}:\n\n{text}"
    )
    await update.message.reply_text(
        "✨Сообщение отправлено!\n\nЖдите ответа в ближайшее время."
    )

app_ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, pre_start), group=0)
app_ptb.add_handler(CommandHandler("start", start_cmd))
app_ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg), group=1)

fast = FastAPI()  # 🔥 ОБЯЗАТЕЛЬНО ДОЛЖНА БЫТЬ ЭТА ПЕРЕМЕННАЯ

@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_ptb.bot.setWebhook(WEBHOOK_URL)
    async with app_ptb:
        await app_ptb.start()
        yield
        await app_ptb.stop()

fast.lifespan = lifespan

@fast.post("/{token}")
async def telegram_webhook(request: Request, token: str):
    if token != BOT_TOKEN.split(":")[0]:
        return Response(status_code=HTTPStatus.FORBIDDEN)
    data = await request.json()
    update = Update.de_json(data, app_ptb.bot)
    await app_ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fast, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
