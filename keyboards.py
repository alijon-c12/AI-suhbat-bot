from telebot import types
from config import BOT_ROLES, IMAGE_STYLES, VIDEO_STYLES


def get_main_keyboard():
    """Doimiy asosiy menyu (ReplyKeyboardMarkup)"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_chat = types.KeyboardButton("💬 AI bilan Suhbat")
    btn_image = types.KeyboardButton("🎨 AI Rasm Chizish")
    btn_video = types.KeyboardButton("🎬 AI Video Yaratish")
    btn_roles = types.KeyboardButton("🎭 Bot Qiyofasi (Rollar)")
    btn_fun = types.KeyboardButton("🎮 Zerikmaslik Menyusi")
    btn_help = types.KeyboardButton("💡 Yordam & Ma'lumot")

    markup.add(btn_chat, btn_image)
    markup.add(btn_video, btn_roles)
    markup.add(btn_fun, btn_help)
    return markup


def get_roles_inline_keyboard(current_role: str = "friend"):
    """Bot qiyofasini (rolini) tanlash inline menyusi"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key, data in BOT_ROLES.items():
        prefix = "✅ " if key == current_role else ""
        text = f"{prefix}{data['icon']} {data['title']}"
        markup.add(types.InlineKeyboardButton(text=text, callback_data=f"role_{key}"))
    return markup


def get_image_styles_keyboard():
    """Rasm uslublarini tanlash inline menyusi"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, data in IMAGE_STYLES.items():
        buttons.append(types.InlineKeyboardButton(text=data["name"], callback_data=f"imgstyle_{key}"))
    markup.add(*buttons)
    return markup


def get_video_styles_keyboard():
    """Video uslublarini tanlash inline menyusi"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key, data in VIDEO_STYLES.items():
        markup.add(types.InlineKeyboardButton(text=data["name"], callback_data=f"vidstyle_{key}"))
    return markup


def get_fun_menu_keyboard():
    """Zerikmaslik uchun interaktiv o'yinlar va qiziqarli bo'limlar"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_fact = types.InlineKeyboardButton("🌍 Qiziqarli Fakt", callback_data="fun_fact")
    btn_joke = types.InlineKeyboardButton("😂 Kulgi & Latifa", callback_data="fun_joke")
    btn_quiz = types.InlineKeyboardButton("🧠 Mantiqiy Savol", callback_data="fun_quiz")
    btn_motivation = types.InlineKeyboardButton("✨ Motivatsiya", callback_data="fun_motivation")
    btn_oracle = types.InlineKeyboardButton("🔮 Sehrli Shar (Bashorat)", callback_data="fun_oracle")
    btn_compliment = types.InlineKeyboardButton("💖 Maqto'v eshitish", callback_data="fun_compliment")
    
    markup.add(btn_fact, btn_joke)
    markup.add(btn_quiz, btn_motivation)
    markup.add(btn_oracle, btn_compliment)
    return markup


def get_chat_actions_keyboard():
    """Har bir AI suhbat xabarining tagida turadigan tezkor amallar"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_clear = types.InlineKeyboardButton("🧹 Xotirani tozalash", callback_data="action_clear")
    btn_role = types.InlineKeyboardButton("🎭 Rolni o'zgartirish", callback_data="action_change_role")
    markup.add(btn_clear, btn_role)
    return markup


def get_cancel_keyboard():
    """Jarayonni bekor qilish tugmasi"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("🔙 Bekor qilish"))
    return markup
