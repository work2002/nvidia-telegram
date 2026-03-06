import os
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
NVIDIA_API_KEY = os.environ["NVIDIA_API_KEY"]

nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
)

# Твоя модель GLM-5
MODEL_NAME = "z-ai/glm5"

chat_histories = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Ты полезный AI-ассистент. Отвечай на Туркмениском языке подробно."
}


def ask_nvidia(chat_id, user_message):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [SYSTEM_PROMPT]

    chat_histories[chat_id].append({
        "role": "user",
        "content": user_message
    })

    if len(chat_histories[chat_id]) > 20:
        chat_histories[chat_id] = (
            [SYSTEM_PROMPT] + chat_histories[chat_id][-19:]
        )

    try:
        response = nvidia_client.chat.completions.create(
            model=MODEL_NAME,
            messages=chat_histories[chat_id],
            temperature=0.6,
            max_tokens=4096,
            top_p=0.7,
        )
        reply = response.choices[0].message.content
        chat_histories[chat_id].append({
            "role": "assistant",
            "content": reply
        })
        return reply
    except Exception as e:
        return f"❌ Ýalňyşlyk: {e}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salam! Men Kesha bot.\n\n"
        "Menden islän zadyňy sorap bilersiň!\n\n"
        "/clear — ýazgylary poz"
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories.pop(update.effective_chat.id, None)
    await update.message.reply_text("🗑 ýazgylar pozuldy.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action("typing")
    reply = ask_nvidia(update.effective_chat.id, update.message.text)

    for i in range(0, len(reply), 4096):
        await update.message.reply_text(reply[i:i + 4096])


def main():
    print("Bot Ýüklenýär...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message
    ))

    print("Bot işledi!")
    app.run_polling()


if __name__ == "__main__":
    main()
