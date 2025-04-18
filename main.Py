 import os
import openai
import re
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta

openai.api_key = os.getenv("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")
TELEGRAM_TOKEN = os.getenv("7784975745:AAHBDFhahq6eI5F6xYUCOr0nxXTkJQsZlgM")
OWNER_NAME = "Rayhan Boss"
reminders = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"হ্যালো {OWNER_NAME}, আমি তোমার AI বন্ধু! প্রশ্ন করো, ছবি আঁকতে বলো, বা রিমাইন্ডার দাও!")

# Message handler
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()

    # শুভ সকাল / রাত্রি
    if "সুপ্রভাত" in user_message or "good morning" in user_message:
        await update.message.reply_text(f"সুপ্রভাত {OWNER_NAME}! আজকের দিনটা হোক অসাধারণ!")
        return
    elif "শুভ রাত্রি" in user_message or "good night" in user_message:
        await update.message.reply_text(f"শুভ রাত্রি {OWNER_NAME}! সুন্দর ঘুম দাও!")
        return

    # রিমাইন্ডার
    match = re.search(r'(\d+)\s*মিনিট.*মনে করিয়ে দিও', user_message)
    if match:
        minutes = int(match.group(1))
        remind_time = datetime.now() + timedelta(minutes=minutes)
        user_id = update.message.chat_id
        reminders[user_id] = (remind_time, "⏰ সময় হয়ে গেছে!")
        await update.message.reply_text(f"{minutes} মিনিট পরে মনে করিয়ে দিবো {OWNER_NAME}।")
        return

    # ছবি তৈরি
    if user_message.startswith(("ছবি", "image", "draw", "generate")):
        try:
            response = openai.Image.create(
                prompt=update.message.text,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            await update.message.reply_photo(photo=image_url, caption="তোমার ছবিটি রেডি!")
        except Exception as e:
            await update.message.reply_text("ছবি তৈরি করতে পারলাম না। আবার চেষ্টা করো।")
        return

    # GPT chat
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"তুমি {OWNER_NAME}-এর AI সহকারী। তুমি বাংলায় ও ইংরেজিতে কথা বলো, বন্ধু হয়ে তার সব প্রশ্নের উত্তর দাও।"},
                {"role": "user", "content": update.message.text}
            ]
        )
        reply = response['choices'][0]['message']['content']
        await update.message.reply_text(reply)
    except:
        await update.message.reply_text("একটু সমস্যা হয়েছে, পরে আবার চেষ্টা করো।")

# Reminder checker
async def reminder_checker(app):
    while True:
        now = datetime.now()
        for user_id, (remind_time, message) in list(reminders.items()):
            if now >= remind_time:
                await app.bot.send_message(chat_id=user_id, text=message)
                del reminders[user_id]
        await asyncio.sleep(5)

# App
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))
app.job_queue.run_once(lambda context: asyncio.create_task(reminder_checker(app)), when=0)

app.run_polling()
