import os
import re
import requests
import time
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ========== CONFIG ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

API_URL = "https://instagram-info-and-downloader.vercel.app/info"

# ========== API CALL ==========
def get_video_url(post_url):
    try:
        resp = requests.get(API_URL, params={"url": post_url}, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data.get('items'):
            return None
        for dl in data['items'][0].get('downloads', []):
            if dl.get('kind') == 'video':
                return dl.get('url')
        return None
    except:
        return None

# ========== DOWNLOAD ==========
def download_file(url, filename):
    try:
        resp = requests.get(url, stream=True, timeout=20)
        if resp.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        return False
    except:
        return False

# ========== BOT HANDLER ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # Only process Instagram links
    if not re.match(r'https?://(www\.)?instagram\.com/(p|reel|tv)/', url):
        return  # Ignore non-Instagram messages
    
    # Get video URL
    video_url = get_video_url(url)
    if not video_url:
        await update.message.reply_text("❌")
        return
    
    # Download
    filename = f"v_{chat_id}_{int(time.time())}.mp4"
    if not download_file(video_url, filename):
        await update.message.reply_text("❌")
        return
    
    # Send video
    try:
        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f, supports_streaming=True)
    except:
        await update.message.reply_text("❌")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# ========== MAIN ==========
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("💀 FUCK 🖕 OFF 📴")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
