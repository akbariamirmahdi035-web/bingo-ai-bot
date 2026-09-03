import asyncio
import logging
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = "8826036160:AAHINDQDP97cvaGF8ezXBni008IyBgq8R9U"
GEMINI_API_KEY = "AQ.Ab8RN6J4NaYxz0qJwesWspD8L0duEnijphcyaNtjzt9hC0ueBw"

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = "You are BinGo AI, a helpful multi-purpose AI assistant. Always respond in Persian unless the user writes in another language."

user_sessions = {}

def get_chat_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        )
    return user_sessions[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BinGo AI - Smarter. Faster. Limitless.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        chat = get_chat_session(user_id)
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Something went wrong.")

def run():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("BinGo AI is running...")
    app.run_polling()

asyncio.set_event_loop(asyncio.new_event_loop())
run()
