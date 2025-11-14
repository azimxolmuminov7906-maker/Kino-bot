import telebot
from telebot import types

TOKEN = "7747848399:AAEyUagn4Vzs5gavfPSSvYrEawV4HjCWn0M"   # bu yerga BotFather bergan tokenni yoz
bot = telebot.TeleBot(TOKEN)

# Faqat SEN (admin) kino biriktira olasin
ADMIN_ID = 7357301935  # bu yerga o'z Telegram ID'ingni yoz

# Obuna bo'lishi shart bo'lgan kanallar ID'lari
KANALLAR = [
    "-1002659417189",
    "-1002873167951",
    "-1002373408190"
]

# Kino bazasi (faqat admin o'zgartira oladi)
KINOLAR = {}

# -------- OBUNA TEKSHIRUV --------

def obuna_bolmaganlar(user_id):
    not_subscribed = []
    for kanal in KANALLAR:
        try:
            a = bot.get_chat_member(kanal, user_id)
            if a.status == "left":
                not_subscribed.append(kanal)
        except:
            not_subscribed.append(kanal)
    return not_subscribed

# -------- START --------

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    user_id = user.id
    username = user.first_name

    not_sub = obuna_bolmaganlar(user_id)

    if not_sub:
        text = f"Xurmatli {username}, botga xush kelibsiz!\n\n"
        text += "Botni ishga tushurish uchun quyidagi kanallarga obuna bo‘ling:\n\n"

        for kanal in not_sub:
            ch = bot.get_chat(kanal)
            text += f"👉 https://t.me/{ch.username}\n"

        btn = types.InlineKeyboardMarkup()
        check_btn = types.InlineKeyboardButton("🔄 Tekshirish", callback_data="check")
        btn.add(check_btn)

        bot.send_message(message.chat.id, text, reply_markup=btn)
    else:
        bot.send_message(message.chat.id,
                         "🎉 Raxmat! Siz barcha kanallarga obuna bo‘lgansiz!\n\nKino kodini yuboring.")

# -------- TEKSHIRISH TUGMASI --------

@bot.callback_query_handler(func=lambda call: call.data == "check")
def tekshirish(call):
    user_id = call.from_user.id
    not_sub = obuna_bolmaganlar(user_id)

    if not_sub:
        text = "❗ Siz hali quyidagi kanallarga obuna bo‘lmadingiz:\n\n"
        for kanal in not_sub:
            ch = bot.get_chat(kanal)
            text += f"👉 https://t.me/{ch.username}\n"

        btn = types.InlineKeyboardMarkup()
        check_btn = types.InlineKeyboardButton("🔄 Qayta tekshirish", callback_data="check")
        btn.add(check_btn)

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              reply_markup=btn)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="🎉 Raxmat! Siz barcha kanallarga obuna bo‘lgansiz!\n\nEndi kino kodini yuboring.")

# -------- ADMIN KINO QO‘SHISH --------

@bot.message_handler(commands=['add'])
def add_kino(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "Bu buyruq faqat admin uchun!")

    try:
        code = message.text.split()[1]
        bot.reply_to(message, f"{code} raqam uchun kino yuboring.")
        bot.register_next_step_handler(message, lambda msg: save_kino(msg, code))
    except:
        bot.reply_to(message, "Namuna: /add 12")


def save_kino(message, code):
    if message.content_type != "video":
        return bot.reply_to(message, "Iltimos, kino faylini video ko‘rinishida yuboring.")

    KINOLAR[code] = message.video.file_id
    bot.reply_to(message, f"{code} kodi uchun kino saqlandi! 🎬")

# -------- FOYDALANUVCHI KOD YUBORSa --------

@bot.message_handler(content_types=['text'])
def kino_ber(message):
    user_id = message.from_user.id
    code = message.text.strip()

    if obuna_bolmaganlar(user_id):
        return start(message)

    if code in KINOLAR:
        bot.send_video(message.chat.id, KINOLAR[code])
    else:
        bot.send_message(message.chat.id, "❗ Bunday kino kodi yo‘q.\nMavjud kodni yuboring.")

bot.infinity_polling()
