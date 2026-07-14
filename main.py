import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp

# === الإعدادات ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@YQ333Y"  # غيره لقناتك
CHANNEL_LINK = "https://t.me/YQ333Y"

# === سيرفر وهمي حتى Koyeb ما يطفي البوت ===
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running!"
@app.route('/ping')
def ping(): return "pong"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
threading.Thread(target=run_flask, daemon=True).start()

# === فحص الاشتراك ===
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member','administrator','creator']
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        keyboard = [[InlineKeyboardButton("اشترك بالقناة 📢", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ تحققت، اشتركت", callback_data="check_sub")]]
        await update.message.reply_text("⚠️ يجب الاشتراك بالقناة لاستخدام البوت", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await update.message.reply_text("أهلاً! أرسل رابط تيك توك، انستا، يوتيوب...")

async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(query.from_user.id, context):
        await query.edit_message_text("تم التفعيل ✅ أرسل الرابط الآن")
    else:
        await query.answer("ما اشتركت بعد!", show_alert=True)

async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await start(update, context); return
    url = update.message.text
    await update.message.reply_text("⏳ جاري التحميل...")
    try:
        ydl_opts = {'format':'best','outtmpl':'%(title)s.%(ext)s','quiet':True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as f:
            await update.message.reply_video(f, caption="تم ✅ @YQ333Y")
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e}")

def main():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(check_sub, pattern="check_sub"))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_handler))
    print("Bot Final Version Running...")
    app_bot.run_polling()

if __name__ == '__main__': main()
