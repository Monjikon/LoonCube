import telebot
from telebot import types
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========================================
# НАСТРОЙКИ — читаются из переменных окружения
# ========================================

TOKEN = os.environ['TELEGRAM_TOKEN']
STAFF_CHAT_ID = int(os.environ['STAFF_CHAT_ID'])
SUPPORT_CHAT_ID = int(os.environ['SUPPORT_CHAT_ID'])
ADMIN_IDS = list(map(int, os.environ['ADMIN_IDS'].split(',')))

SERVER_IP = os.environ.get('SERVER_IP', 'your.server.ip')
SERVER_VERSION = os.environ.get('SERVER_VERSION', '1.20.x')
SERVER_DISCORD = os.environ.get('SERVER_DISCORD', 'discord.gg/yourserver')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '@YourAdminUsername')

# ========================================

bot = telebot.TeleBot(TOKEN)
user_states = {}

MENU_BUTTONS = [
    '📋 Анкета для Команды проекта',
    '🎥 Анкета для YouTube',
    '📱 Анкета для TikTok',
    '⚠️ Жалоба',
    '👤 Жалоба на игрока',
    '👮 Жалоба на персонал',
    '🛠 Техническая поддержка',
    '❓ Помощь',
    '🔙 Назад',
]

def get_admin_help_text():
    return (
        "👨‍💼 *АДМИН КОМАНДЫ*\n\n"
        "📝 `/reply <user_id> <текст>`\n"
        "Ответить конкретному пользователю\n"
        "Пример: `/reply 123456789 Ваша заявка одобрена!`\n\n"
        "📢 `/broadcast <текст>`\n"
        "Массовая рассылка (требует базы данных — пока не реализовано)\n\n"
        "ℹ️ `/help`\n"
        "Показать эту справку\n\n"
        "💡 *Совет:* ID пользователя есть в каждом пересланном запросе!"
    )

def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('📋 Анкета для Команды проекта'),
        types.KeyboardButton('🎥 Анкета для YouTube'),
        types.KeyboardButton('📱 Анкета для TikTok'),
        types.KeyboardButton('⚠️ Жалоба'),
        types.KeyboardButton('🛠 Техническая поддержка'),
        types.KeyboardButton('❓ Помощь')
    )
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в бот Minecraft сервера!\n\n"
        "Выберите опцию ниже:",
        reply_markup=markup
    )

@bot.message_handler(commands=['start'])
def start_message(message):
    user_states.pop(message.chat.id, None)
    if message.chat.id in ADMIN_IDS:
        bot.send_message(
            message.chat.id,
            "👨‍💼 *АДМИН ПАНЕЛЬ*\n\n"
            "Доступные команды:\n"
            "/reply <user_id> <сообщение> — Ответить пользователю\n"
            "/broadcast <сообщение> — Отправить всем (требует БД)\n"
            "/help — Показать эту справку\n\n"
            "Пример:\n"
            "`/reply 123456789 Ваша заявка принята!`",
            parse_mode='Markdown'
        )
        return
    show_main_menu(message)

@bot.message_handler(commands=['reply'])
def reply_to_user(message):
    if message.chat.id not in ADMIN_IDS:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Формат: `/reply <user_id> <сообщение>`", parse_mode='Markdown')
        return
    try:
        user_id = int(parts[1])
        reply_text = parts[2]
        if user_id in ADMIN_IDS:
            bot.send_message(message.chat.id, "⚠️ Вы пытаетесь ответить другому администратору. Это не рекомендуется.")
            return
        bot.send_message(user_id, f"📨 *Ответ от администрации:*\n\n{reply_text}", parse_mode='Markdown')
        bot.send_message(message.chat.id, f"✅ Сообщение успешно отправлено пользователю {user_id}")
        logger.info(f"Admin {message.chat.id} replied to {user_id}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный ID пользователя. Убедитесь, что ID — это число.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при отправке: {e}")
        logger.error(f"Error replying to {user_id}: {e}")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.chat.id not in ADMIN_IDS:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: `/broadcast <сообщение>`", parse_mode='Markdown')
        return
    bot.send_message(
        message.chat.id,
        "⚠️ Функция массовой рассылки требует базы данных пользователей.\n"
        "Сейчас она не реализована — используйте `/reply <user_id> <текст>` для индивидуальных ответов.",
        parse_mode='Markdown'
    )
    logger.info(f"Admin {message.chat.id} tried to broadcast, but feature is disabled")

@bot.message_handler(commands=['help'])
def help_admin(message):
    if message.chat.id not in ADMIN_IDS:
        return
    bot.send_message(message.chat.id, get_admin_help_text(), parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '📋 Анкета для Команды проекта')
def project_team_request(message):
    user_states[message.chat.id] = 'awaiting_project_application'
    application_text = (
        "📋 *АНКЕТА ДЛЯ КОМАНДЫ ПРОЕКТА*\n\n"
        "Советуем ознакомиться с требованиями!\n\n"
        "✅ Свободное владение русским языком.\n"
        "✅ Умение эффективно взаимодействовать с сообществом игроков.\n"
        "✅ Базовые знания команд помощника.\n"
        "✅ Возраст от 14 лет (возможны исключения).\n"
        "✅ Отсутствие жалоб и нарушений на игровом аккаунте.\n"
        "✅ Готовность серьёзно относиться к выполнению обязанностей.\n"
        "✅ Понимание основных команд сервера.\n\n"
        "📌 *Формат подачи заявок строго регламентирован:*\n\n"
        "1️⃣ Игровой никнейм.\n"
        "2️⃣ Текущая игровая привилегия.\n"
        "3️⃣ Полных лет.\n"
        "4️⃣ Длительность знакомства с нашим проектом.\n"
        "5️⃣ Сколько времени в сутки вы готовы уделять проекту?\n"
        "6️⃣ Перечислите предыдущие игровые проекты, где вы приобрели опыт модерирования.\n"
        "7️⃣ Кратко опишите себя минимум в 40 словах.\n"
        "⭐ Оценка уровня владения правилами сервера по пятибалльной шкале. (1/5)\n\n"
        "🔍 Все заявки внимательно изучаются командой ежедневно. Отбор проходят только самые достойные кандидаты.\n\n"
        "🛑 Запрещено писать личное сообщение администраторам относительно статуса заявки. Несоблюдение приведёт к автоматическому отказу.\n\n"
        "➡️ Теперь отправьте вашу заявку в соответствии с форматом выше:"
    )
    bot.send_message(message.chat.id, application_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '🎥 Анкета для YouTube')
def youtube_application(message):
    user_states[message.chat.id] = 'awaiting_youtube_application'
    youtube_text = (
        "🎥 *АНКЕТА ДЛЯ YOUTUBE*\n\n"
        "✅ *Критерии для категории MEDIA:*\n\n"
        "👉 Минимум 50 подписчиков на твоём YouTube-канале. Исключения возможны.\n"
        "👉 От 50 просмотров за каждые полные сутки.\n"
        "👉 Тематика роликов должна соответствовать игре MINECRAFT.\n"
        "👉 Нет проблем с каналом со стороны администрации.\n"
        "👉 Наличие хотя бы одного видеоролика, записанного на нашем сервере.\n\n"
        "✅ *Критерии для категории MEDIA+:*\n\n"
        "👉 Минимум 250 подписчиков на твоём YouTube-канале. Возможны исключения.\n"
        "👉 Ежедневно должно быть не менее 150 просмотров.\n"
        "👉 Обязательная тематика роликов — игра MINECRAFT.\n"
        "👉 Канал должен быть чист перед администрацией.\n"
        "👉 Обязательно наличие видео, отснятых на нашем проекте.\n\n"
        "Если вы подходите по критериям, можете уверенно писать заявку!\n\n"
        "📋 *Форма заявки:*\n\n"
        "🎯 Игровой никнейм:\n"
        "🧑‍🤝‍🧑 Желаемый уровень: YT / YT+\n"
        "🌐 Ссылка на ваш YouTube-канал:\n"
        "📹 Ссылка на примеры ваших работ:\n\n"
        "❗ *ВАЖНО:* Если ты перестанешь выкладывать контент четыре дня подряд, права участника будут отозваны.\n\n"
        "➡️ Теперь отправьте вашу заявку:"
    )
    bot.send_message(message.chat.id, youtube_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '📱 Анкета для TikTok')
def tiktok_application(message):
    user_states[message.chat.id] = 'awaiting_tiktok_application'
    tiktok_text = (
        "📱 *АНКЕТА ДЛЯ TIKTOK*\n\n"
        "🌟 *КРИТЕРИИ ДЛЯ УЧАСТИЯ:*\n\n"
        "🎬 *Категория TIKTOK:*\n\n"
        "📍 Адекватность поведения, ответственность и умение общаться.\n"
        "📍 Каждый ролик должен получать минимум 150 просмотров.\n"
        "📍 Количество подписчиков — от 80+.\n"
        "📍 Наличие ролика, снятого на нашем сервере.\n\n"
        "🌟 *Категория TIKTOK PLUS+:*\n\n"
        "📍 Такие же требования по адекватности и качеству общения.\n"
        "📍 Ролики обязаны собирать не меньше 550 просмотров.\n"
        "📍 Подписчиков должно быть не менее 300+.\n"
        "📍 Необходим хотя бы один качественный ролик, сделанный на нашем сервере.\n\n"
        "📋 *ФОРМА ЗАЯВКИ:*\n\n"
        "🖼️ Игровой никнейм:\n"
        "📊 Желаемый уровень: TT / TT+\n"
        "🏷️ Ссылка на ваш аккаунт TikTok:\n"
        "📱 Ссылка на видео с нашим сервером:\n"
        "🔗 Профиль в TikTok (IP в описании):\n\n"
        "📌 *Важно:* запрет на спамирование сообщений администраторам. Нарушение приведёт к автоматической отмене заявки.\n\n"
        "➡️ Теперь отправьте вашу заявку:"
    )
    bot.send_message(message.chat.id, tiktok_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '⚠️ Жалоба')
def complaint_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('👤 Жалоба на игрока'))
    markup.add(types.KeyboardButton('👮 Жалоба на персонал'))
    markup.add(types.KeyboardButton('🔙 Назад'))
    bot.send_message(
        message.chat.id,
        "⚠️ *ПОДАЧА ЖАЛОБЫ*\n\nВыберите тип жалобы:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: m.text == '👤 Жалоба на игрока')
def player_complaint(message):
    user_states[message.chat.id] = 'awaiting_player_complaint'
    complaint_text = (
        "👤 *ЖАЛОБА НА ИГРОКА*\n\n"
        "Жалоба должна заполняться СТРОГО по форме ниже.\n\n"
        "📋 *ФОРМА:*\n\n"
        "🔹 Ваш никнейм на сервере\n"
        "🔹 Никнейм нарушителя\n"
        "🔹 Пункт правил, по которому было нарушение\n"
        "🔹 Описание нарушения\n"
        "🔹 Доказательства (Видео/скриншот)\n\n"
        "⚠️ Принимаются доказательства, загруженные в ВК, YouTube, Imgur.\n"
        "❌ Доказательства со сторонних ресурсов не рассматриваются!\n\n"
        "➡️ Теперь отправьте вашу жалобу:"
    )
    bot.send_message(message.chat.id, complaint_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '👮 Жалоба на персонал')
def staff_complaint(message):
    user_states[message.chat.id] = 'awaiting_staff_complaint'
    complaint_text = (
        "👮 *ЖАЛОБА НА ПЕРСОНАЛ*\n\n"
        "▪ *Форма подачи жалобы:*\n\n"
        "🔹 Ваш никнейм.\n"
        "🔹 Никнейм нарушителя с должностью (Хелпер, ст.Хелпер, Модератор, ст.Модератор).\n"
        "🔹 Суть нарушения.\n"
        "🔹 Пункт правил, который нарушили.\n"
        "🔹 Доказательства нарушения.\n\n"
        "⚠️ Заявка подаётся строго по форме выше.\n"
        "⚠️ Если после момента нарушения прошло более 3-х дней, жалоба будет отклонена.\n\n"
        "➡️ Теперь отправьте вашу жалобу:"
    )
    bot.send_message(message.chat.id, complaint_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '🛠 Техническая поддержка')
def tech_support_request(message):
    user_states[message.chat.id] = 'awaiting_support_request'
    bot.send_message(
        message.chat.id,
        "🛠 *Техническая поддержка*\n\n"
        "Пожалуйста, опишите вашу проблему.\n"
        "Укажите:\n"
        "• Ваш игровой никнейм\n"
        "• Что именно произошло\n"
        "• Когда это произошло",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: m.text == '❓ Помощь')
def help_command(message):
    help_text = (
        "🎮 *Помощь по боту Minecraft сервера*\n\n"
        "📋 *Команда проекта* — подать заявку в команду\n\n"
        "🎥 *Анкета для YouTube / TikTok* — получить медиа-привилегии\n\n"
        "⚠️ *Жалоба* — пожаловаться на игрока или персонал\n\n"
        "🛠 *Техническая поддержка* — сообщить о баге или проблеме\n\n"
        "❓ *Помощь* — показать это сообщение\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "*Информация о сервере:*\n"
        f"• IP: `{SERVER_IP}`\n"
        f"• Версия: {SERVER_VERSION}\n"
        f"• Discord: {SERVER_DISCORD}\n\n"
        f"Нужна дополнительная помощь? Свяжитесь с {ADMIN_USERNAME}"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '🔙 Назад')
def back_to_menu(message):
    user_states.pop(message.chat.id, None)
    show_main_menu(message)

@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def handle_requests(message):
    user_id = message.chat.id
    username = message.from_user.username or message.from_user.first_name

    if message.content_type == 'text' and message.text in MENU_BUTTONS:
        return

    if user_id not in user_states:
        bot.send_message(user_id, "⬇️ Пожалуйста, воспользуйтесь меню ниже. Нажмите /start для перезапуска.")
        return

    if message.content_type == 'text' and not message.text.strip():
        bot.send_message(user_id, "❌ Пожалуйста, отправьте корректное сообщение.")
        return

    state = user_states[user_id]
    state_labels = {
        'awaiting_project_application': '📋 Анкета для Команды проекта',
        'awaiting_youtube_application': '🎥 Анкета YouTube',
        'awaiting_tiktok_application': '📱 Анкета TikTok',
        'awaiting_player_complaint': '👤 Жалоба на игрока',
        'awaiting_staff_complaint': '👮 Жалоба на персонал',
        'awaiting_support_request': '🛠 Техническая поддержка',
    }

    is_support = (state == 'awaiting_support_request')
    target_chat = SUPPORT_CHAT_ID if is_support else STAFF_CHAT_ID

    request_header = (
        f"📩 *Новый запрос*\n"
        f"От: @{username} (ID: `{user_id}`)\n"
        f"Тип: {state_labels.get(state, 'Неизвестно')}\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"Для ответа:\n"
        f"`/reply {user_id} Ваш ответ здесь`\n\n"
    )

    try:
        if message.content_type == 'text':
            bot.send_message(target_chat, request_header + message.text.strip(), parse_mode='Markdown')
        elif message.content_type == 'photo':
            bot.send_photo(target_chat, message.photo[-1].file_id,
                           caption=request_header + (message.caption or '').strip(),
                           parse_mode='Markdown')
        elif message.content_type == 'video':
            bot.send_video(target_chat, message.video.file_id,
                           caption=request_header + (message.caption or '').strip(),
                           parse_mode='Markdown')
        elif message.content_type == 'document':
            bot.send_document(target_chat, message.document.file_id,
                              caption=request_header + (message.caption or '').strip(),
                              parse_mode='Markdown')

        confirm = (
            "✅ Ваш запрос в поддержку отправлен! Наша команда скоро ответит."
            if is_support else
            "✅ Ваша заявка/жалоба отправлена! Ожидайте ответа."
        )
        bot.send_message(user_id, confirm)
        user_states.pop(user_id, None)
        logger.info(f"Request from {user_id} ({state}) sent to {target_chat}")

    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ Ошибка при отправке: {e}\n\nОставайтесь в состоянии — попробуйте отправить ещё раз."
        )
        logger.error(f"Failed to send request from {user_id}: {e}")

if __name__ == '__main__':
    logger.info("🤖 Бот успешно запущен! Ждём запросы...")
    print("🤖 Бот успешно запущен! Нажмите Ctrl+C для остановки.")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
