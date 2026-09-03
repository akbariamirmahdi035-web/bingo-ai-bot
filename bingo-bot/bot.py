import asyncio
import logging
import os
import sys
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = "8826036160:AAHINDQDP97cvaGF8ezXBni008IyBgq8R9U"
GEMINI_API_KEY = "AQ.Ab8RN6J4NaYxz0qJwesWspD8L0duEnijphcyaNtjzt9hC0ueBw"
OWNER_ID = 8660964764

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = "You are BinGo AI, a helpful multi-purpose AI assistant. Always respond in Persian unless the user writes in another language."

user_sessions = {}
pending_code = {}

def get_chat_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        )
    return user_sessions[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BinGo AI - Smarter. Faster. Limitless.")

async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("??? ????? ??? ???? ???? ??? ?????.")
        return

    request_text = update.message.text.replace("/update", "").strip()
    if not request_text:
        await update.message.reply_text("????? ????? ??? ?? ?????? ???????.")
        return

    await update.message.reply_text("?? ??? ????? ?? ????... ??? ???? ??? ??")

    with open(__file__, "r", encoding="utf-8") as f:
        current_code = f.read()

    prompt = "This is the current Python code of a Telegram bot:\n\n" + current_code + "\n\nThe user wants this change: " + request_text + "\n\nReturn ONLY the complete, full updated Python file content, with no explanation, no markdown code fences, nothing else. The file must remain fully runnable as-is."

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        new_code = response.text.strip()
        if new_code.startswith("```"):
            new_code = new_code.split("```")[1]
            if new_code.startswith("python"):
                new_code = new_code[6:]
        pending_code[user_id] = new_code.strip()

        preview = new_code[:3000]
        await update.message.reply_text("?? ???? ????? ??. ??? ???????????:\n\n" + preview)
        await update.message.reply_text("??? ????? ?????? ?????: ?????")
    except Exception as e:
        logging.error("Update error: " + str(e))
        await update.message.reply_text("??? ?? ???? ?? ????.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_text.strip() == "?????" and user_id == OWNER_ID and user_id in pending_code:
        try:
            with open(__file__, "w", encoding="utf-8") as f:
                f.write(pending_code[user_id])
            await update.message.reply_text("??????????? ????? ??. ??? ?? ??? ?????????...")
            del pending_code[user_id]
            python = sys.executable
            os.execl(python, python, __file__)
        except Exception as e:
            logging.error("Apply error: " + str(e))
            await update.message.reply_text("??? ?? ????? ???????????.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        chat = get_chat_session(user_id)
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error("Error: " + str(e))
        await update.message.reply_text("Something went wrong.")

def run():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("BinGo AI is running...")
    app.run_polling()

asyncio.set_event_loop(asyncio.new_event_loop())
run()