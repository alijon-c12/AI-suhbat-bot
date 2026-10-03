import os
import threading
from flask import Flask, request, jsonify

import telebot

# Import bot instance and webhook setter from main
from main import bot, set_telegram_webhook

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
            app.logger.error(f"Failed to process Telegram update: {e}")
        return "", 200
    # Simple health endpoint for Render
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Set the Telegram webhook in a background thread
    threading.Thread(target=set_telegram_webhook, daemon=True).start()
    # Render provides PORT env variable (fallback to 8080 for local tests)
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
