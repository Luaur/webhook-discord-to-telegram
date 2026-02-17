from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- KONFIGURASI ---
# Ganti dengan Token dan Chat ID Telegram kamu
TELEGRAM_BOT_TOKEN = os.environ.get('TG_TOKEN', 'TOKEN_BOT_KAMU_DISINI')
TELEGRAM_CHAT_ID = os.environ.get('TG_CHAT_ID', 'CHAT_ID_KAMU_DISINI')

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown', # Supaya bisa Bold/Italic
        'disable_web_page_preview': True
    }
    requests.post(url, json=payload)

@app.route('/discord-adapter', methods=['POST'])
def discord_to_telegram():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data"}), 400

        # --- LOGIKA PENERJEMAH (DISCORD -> TELEGRAM) ---
        telegram_msg = ""

        # 1. Ambil Username (jika ada)
        username = data.get('username', 'Roblox Bot')
        telegram_msg += f"🤖 *{username}*\n\n"

        # 2. Ambil Pesan Utama (Content)
        if 'content' in data and data['content']:
            telegram_msg += f"{data['content']}\n\n"

        # 3. Ambil Embeds (Kotak Info Discord)
        # Discord bisa kirim banyak embed sekaligus, kita loop semuanya
        if 'embeds' in data:
            for embed in data['embeds']:
                # Judul Embed
                if 'title' in embed:
                    telegram_msg += f"📌 *{embed['title']}*\n"
                
                # Deskripsi Embed
                if 'description' in embed:
                    telegram_msg += f"_{embed['description']}_\n"
                
                telegram_msg += "\n" # Spasi

                # Fields (Bagian paling penting agar rapi)
                if 'fields' in embed:
                    for field in embed['fields']:
                        name = field.get('name', '-')
                        value = field.get('value', '-')
                        # Format: • Nama: Isi
                        telegram_msg += f"• *{name}:* {value}\n"
                    telegram_msg += "\n"

                # Footer
                if 'footer' in embed:
                    footer_text = embed['footer'].get('text', '')
                    telegram_msg += f"└ 🕒 {footer_text}\n"

                telegram_msg += "━━━━━━━━━━━━━━\n"

        # Kirim hasil terjemahan ke Telegram
        send_to_telegram(telegram_msg)
        
        return jsonify({"status": "converted & sent"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Wajib untuk Vercel
if __name__ == '__main__':
    app.run()
