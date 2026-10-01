import threading
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({"status": "ok"})

def run_bot():
    # Import inside function to avoid double initialization
    from main import start_bot
    start_bot()

if __name__ == '__main__':
    # Start the bot in a daemon thread so Flask can serve requests
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    # Render provides PORT env variable
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
