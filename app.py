import logging
import os
import threading

import telebot
from flask import Flask, jsonify, request

# Import bot instance and webhook setter from main
from main import bot, set_telegram_webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AppEntry")

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def webhook():
    """Health check (GET) and Telegram webhook (POST)."""
    if request.method == "POST":
        json_str = request.get_data(as_text=True)
        try:
            update = telebot.types.Update.de_json(json_str)
            bot.process_new_updates([update])
        except Exception as e:
            logger.error("Telegram update qayta ishlashda xatolik: %s", e)
        return "", 200
    # Render health check
    return jsonify({"status": "ok", "bot": "running"})


# ========================================================
# Gunicorn yoki python app.py orqali ishlaganda ham ishlaydi
# ========================================================
def _start_webhook_thread():
    """Webhook ni fon threadida o'rnatadi."""
    try:
        set_telegram_webhook()
        logger.info("Webhook muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        logger.error("Webhook o'rnatishda xatolik: %s", e)


# Module darajasida chaqiriladi – gunicorn import qilganda ham ishlaydi
threading.Thread(target=_start_webhook_thread, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info("Flask server port %s da ishga tushmoqda...", port)
    app.run(host="0.0.0.0", port=port)
