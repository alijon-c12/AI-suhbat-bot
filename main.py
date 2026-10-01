import html
import logging
import os
import random
import threading
import time
from pathlib import Path

import telebot
from telebot import types

import config
from ai_engine import (
    ask_ai_chat,
    clear_user_history,
    generate_ai_image,
    generate_ai_video,
    get_user_role,
    set_user_role,
)
from keyboards import (
    get_cancel_keyboard,
    get_chat_actions_keyboard,
    get_fun_menu_keyboard,
    get_image_styles_keyboard,
    get_main_keyboard,
    get_roles_inline_keyboard,
    get_video_styles_keyboard,
)

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AIBot")

# Token tekshiruvi
TOKEN = config.BOT_TOKEN
if not TOKEN:
    print("\n" + "=" * 60)
    print("DIQQAT: TELEGRAM_BOT_TOKEN topilmadi!")
    print("Iltimos, '.env' faylini ochib bot tokeningizni kiriting:")
    print("TELEGRAM_BOT_TOKEN=sizning_bot_tokeningiz")
    print("=" * 60 + "\n")
    # Tizim xatolik bermasdan foydalanuvchiga xabar berishi uchun vaqtinchalik xabardor qilamiz
    raise RuntimeError("TELEGRAM_BOT_TOKEN o'rnatilmagan. Iltimos, .env faylida tokenni belgilang.")

bot = telebot.TeleBot(TOKEN, parse_mode=None)

# Foydalanuvchilarning vaqtinchalik holatlari (FSM)
# user_id -> {"state": "waiting_image_prompt", "style": "realistic", ...}
USER_STATES = {}
STATE_LOCK = threading.RLock()


def get_user_state(user_id: int):
    with STATE_LOCK:
        return USER_STATES.get(user_id, {})


def set_user_state(user_id: int, state_data: dict):
    with STATE_LOCK:
        USER_STATES[user_id] = state_data


def clear_user_state(user_id: int):
    with STATE_LOCK:
        if user_id in USER_STATES:
            del USER_STATES[user_id]


# ==========================================
# /start va ASOSIY BUYRUQLAR
# ==========================================

@bot.message_handler(commands=["start"])
def cmd_start(message: types.Message):
    user_id = message.chat.id
    clear_user_state(user_id)
    user_name = html.escape(message.from_user.first_name or "qadrdonim")
    
    welcome_msg = (
        f"👋 <b>Assalomu alaykum, {user_name}!</b>\n\n"
        f"✨ Men sizning <b>Super AI Hamrohingizman</b>! 🤖\n\n"
        f"Siz bilan qiziqarli suhbat quraman, hech qachon zeriktirmayman va istalgan vazifangizda xizmat qilaman:\n\n"
        f"💬 <b>AI Suhbat</b> — Savollarga javob, maslahat, do'stona muloqot\n"
        f"🎨 <b>AI Rasm</b> — Har qanday tasavvuringizni rasmga aylantirish (Flux HD)\n"
        f"🎬 <b>AI Video</b> — So'rovingiz bo'yicha kinematik video roliklar\n"
        f"🎭 <b>Bot Qiyofasi</b> — AI xarakterini o'zgartirish (Do'st, Psixolog, Dasturchi...)\n"
        f"🎮 <b>Zerikmaslik Menyusi</b> — Viktorinalar, latifalar, bashorat va o'yinlar\n\n"
        f"👇 <i>Quyidagi menyudan o'zingizga kerakli bo'limni tanlang:</i>"
    )
    bot.send_message(user_id, welcome_msg, parse_mode="HTML", reply_markup=get_main_keyboard())


@bot.message_handler(commands=["help"])
def cmd_help(message: types.Message):
    user_id = message.chat.id
    help_text = (
        "💡 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "🔹 <b>Oddiy muloqot:</b> Menga shunchaki xabar yozing — men sizga aqlli do'st sifatida javob qaytaraman.\n"
        "🔹 <b>Rasm chizish:</b> '🎨 AI Rasm Chizish' tugmasini bosing yoki /image buyrug'ini yuboring.\n"
        "🔹 <b>Video yaratish:</b> '🎬 AI Video Yaratish' tugmasini bosing yoki /video buyrug'ini yuboring.\n"
        "🔹 <b>Xarakterlar:</b> '🎭 Bot Qiyofasi' orqali botni dasturchi, psixolog yoki hazilkashga aylantiring.\n"
        "🔹 <b>Xotirani tozalash:</b> Yangi mavzuni noldan boshlash uchun /clear buyrug'idan foydalaning.\n\n"
        "🚀 <i>Har qanday g'oya, reja yoki muammongiz bo'lsa, bemalol so'rang!</i>"
    )
    bot.send_message(user_id, help_text, parse_mode="HTML", reply_markup=get_main_keyboard())


@bot.message_handler(commands=["clear", "reset"])
def cmd_clear(message: types.Message):
    user_id = message.chat.id
    clear_user_history(user_id)
    clear_user_state(user_id)
    bot.send_message(
        user_id,
        "🧹 <b>Suhbat xotirasi tozalandi!</b>\nEndi yangi mavzuda suhbatlashishimiz mumkin. Nimalar haqida gaplashamiz? 😊",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(commands=["image"])
def cmd_image(message: types.Message):
    user_id = message.chat.id
    clear_user_state(user_id)
    bot.send_message(
        user_id,
        "🎨 <b>AI Rasm Chizish bo'limi</b>\n\nAvval qaysi uslubda rasm yaratmoqchisiz, tanlang:",
        parse_mode="HTML",
        reply_markup=get_image_styles_keyboard()
    )


@bot.message_handler(commands=["video"])
def cmd_video(message: types.Message):
    user_id = message.chat.id
    clear_user_state(user_id)
    bot.send_message(
        user_id,
        "🎬 <b>AI Video Yaratish bo'limi</b>\n\nVideo uchun kinematik yo'nalishni tanlang:",
        parse_mode="HTML",
        reply_markup=get_video_styles_keyboard()
    )


@bot.message_handler(commands=["roles"])
def cmd_roles(message: types.Message):
    user_id = message.chat.id
    current_role = get_user_role(user_id)
    bot.send_message(
        user_id,
        "🎭 <b>Bot Qiyofasini (Xarakterini) tanlang:</b>\n\n"
        "Siz bilan kim suhbatlashishini xohlaysiz?",
        parse_mode="HTML",
        reply_markup=get_roles_inline_keyboard(current_role)
    )


# ==========================================
# REPLY MENYU BOSHQARUVI
# ==========================================

@bot.message_handler(func=lambda msg: msg.text in [
    "💬 AI bilan Suhbat",
    "🎨 AI Rasm Chizish",
    "🎬 AI Video Yaratish",
    "🎭 Bot Qiyofasi (Rollar)",
    "🎮 Zerikmaslik Menyusi",
    "💡 Yordam & Ma'lumot",
    "🔙 Bekor qilish"
])
def handle_menu_buttons(message: types.Message):
    user_id = message.chat.id
    text = message.text

    if text == "🔙 Bekor qilish":
        clear_user_state(user_id)
        bot.send_message(user_id, "Amal bekor qilindi. Bosh menyudasiz 👇", reply_markup=get_main_keyboard())
        return

    if text == "💬 AI bilan Suhbat":
        role_key = get_user_role(user_id)
        role_info = config.BOT_ROLES.get(role_key, config.BOT_ROLES["friend"])
        bot.send_message(
            user_id,
            f"💬 <b>AI Suhbat faol!</b>\n\nHozirgi rejim: <b>{role_info['title']}</b>\n"
            f"<i>{role_info['description']}</i>\n\n"
            f"Istalgan savolingizni yoki fikringizni yozing, birga suhbatlashamiz! ✨",
            parse_mode="HTML",
            reply_markup=get_chat_actions_keyboard()
        )

    elif text == "🎨 AI Rasm Chizish":
        cmd_image(message)

    elif text == "🎬 AI Video Yaratish":
        cmd_video(message)

    elif text == "🎭 Bot Qiyofasi (Rollar)":
        cmd_roles(message)

    elif text == "🎮 Zerikmaslik Menyusi":
        bot.send_message(
            user_id,
            "🎮 <b>Zerikishga qarshi interaktiv bo'lim!</b>\n\n"
            "Kayfiyatingizni ko'tarish uchun quyidagilardan birini tanlang:",
            parse_mode="HTML",
            reply_markup=get_fun_menu_keyboard()
        )

    elif text == "💡 Yordam & Ma'lumot":
        cmd_help(message)


# ==========================================
# CALLBACK QUERY BOSHQARUVI (INLINE TUGMALAR)
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call: types.CallbackQuery):
    user_id = call.message.chat.id
    data = call.data

    try:
        # Rol o'zgartirish
        if data.startswith("role_"):
            new_role = data.replace("role_", "")
            set_user_role(user_id, new_role)
            role_data = config.BOT_ROLES.get(new_role, config.BOT_ROLES["friend"])
            bot.answer_callback_query(call.id, text=f"Rol tanlandi: {role_data['title']}")
            bot.edit_message_text(
                f"✅ Bot qiyofasi o'zgardi:\n\n<b>{role_data['title']}</b>\n\n"
                f"<i>{role_data['description']}</i>\n\n"
                f"Endi bemalol o'z savol va fikrlaringizni yozavering!",
                chat_id=user_id,
                message_id=call.message.message_id,
                parse_mode="HTML"
            )

        # Rasm uslubini tanlash
        elif data.startswith("imgstyle_"):
            style_key = data.replace("imgstyle_", "")
            style_name = config.IMAGE_STYLES.get(style_key, {}).get("name", "Tanlangan uslub")
            set_user_state(user_id, {"state": "waiting_image_prompt", "style": style_key})
            
            bot.answer_callback_query(call.id)
            bot.send_message(
                user_id,
                f"🎨 Uslub tanlandi: <b>{style_name}</b>\n\n"
                f"✍️ <b>Endi chizmoqchi bo'lgan rasmingizni tasvirlab bering:</b>\n"
                f"<i>Masalan: Toshkent osmonida uchayotgan futuristik kema yoki dengiz sohilidagi qasr</i>",
                parse_mode="HTML",
                reply_markup=get_cancel_keyboard()
            )

        # Video uslubini tanlash
        elif data.startswith("vidstyle_"):
            style_key = data.replace("vidstyle_", "")
            style_name = config.VIDEO_STYLES.get(style_key, {}).get("name", "Kinematik")
            set_user_state(user_id, {"state": "waiting_video_prompt", "style": style_key})
            
            bot.answer_callback_query(call.id)
            bot.send_message(
                user_id,
                f"🎬 Yo'nalish tanlandi: <b>{style_name}</b>\n\n"
                f"✍️ <b>Video uchun g'oya yoki manzarani yozing:</b>\n"
                f"<i>Masalan: Quyosh botayotgan paytdagi sokin ko'l va tog'lar yoki kiberpank shahar ko'chalari</i>",
                parse_mode="HTML",
                reply_markup=get_cancel_keyboard()
            )

        # Suhbat harakatlari
        elif data == "action_clear":
            clear_user_history(user_id)
            bot.answer_callback_query(call.id, text="Xotira tozalandi!")
            bot.send_message(user_id, "🧹 Suhbat xotirasi tozalandi. Yangi suhbatni boshlaymiz!")

        elif data == "action_change_role":
            bot.answer_callback_query(call.id)
            cmd_roles(call.message)

        # Zerikmaslik menyusi amallari
        elif data.startswith("fun_"):
            fun_type = data.replace("fun_", "")
            bot.answer_callback_query(call.id, text="AI tayyorlamoqda...")
            bot.send_chat_action(user_id, "typing")

            prompts = {
                "fact": "Foydalanuvchiga dunyodagi juda g'aroyib, aql bovar qilmas va qiziqarli ilmiy yoki tarixiy fakt aytib ber. O'zbek tilida, qiziqarli emojilar bilan.",
                "joke": "Foydalanuvchining kayfiyatini ko'taradigan juda kulgili, zamonaviy va samimiy latifa yoki qisqa hangoma aytib ber. O'zbek tilida.",
                "quiz": "Foydalanuvchiga fikrlashni talab qiladigan qiziqarli mantiqiy topishmoq yoki viktorina savoli ber. (Javobini pastda yashirin yoki keyinroq aytishingni bildir).",
                "motivation": "Bugun uchun kuchli, ilhomlantiruvchi va qalbga yetib boradigan shaxsiy motivatsiya va tavsiya yoz. O'zbek tilida.",
                "oracle": "Sehrli bashorat shari (Magic 8-Ball) qiyofasida foydalanuvchiga bugungi kuni yoki kelajagi haqida quvnoq, sirli va ijobiy bashorat ber.",
                "compliment": "Foydalanuvchiga o'ziga xos, samimiy va chiroyli kompliment (maqtov) ayt, u o'zini qadrli his qilsin."
            }
            prompt = prompts.get(fun_type, "Menga qiziqarli narsa aytib ber.")
            result = ask_ai_chat(user_id, prompt)
            bot.send_message(user_id, result, reply_markup=get_fun_menu_keyboard())

    except Exception as e:
        logger.error("Callback xatosi: %s", e)
        bot.answer_callback_query(call.id, text="Kichik xatolik yuz berdi.")


# ==========================================
# FOYDALANUVCHI MATNLI XABARLARINI QAYTA ISHLASH
# ==========================================

@bot.message_handler(func=lambda msg: True, content_types=["text"])
def handle_all_text(message: types.Message):
    user_id = message.chat.id
    user_text = message.text.strip()
    state = get_user_state(user_id)

    # 1. Rasm chizish kutilayotgan bo'lsa
    if state.get("state") == "waiting_image_prompt":
        clear_user_state(user_id)
        style = state.get("style", "realistic")
        
        status_msg = bot.send_message(
            user_id,
            "🎨 <b>Rassom AI ishga tushdi...</b>\n<i>G'oyangiz bo'yicha yuqori sifatli rasm chizilmoqda, kuting...</i> ⏳",
            parse_mode="HTML"
        )
        bot.send_chat_action(user_id, "upload_photo")

        def run_image_generation():
            try:
                img_url = generate_ai_image(user_text, style_key=style)
                caption = f"✨ <b>Sizning AI rasmingiz tayyor!</b>\n\n📝 <i>So'rov:</i> {html.escape(user_text)}"
                bot.send_photo(
                    user_id,
                    photo=img_url,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=get_main_keyboard()
                )
                try:
                    bot.delete_message(user_id, status_msg.message_id)
                except Exception:
                    pass
            except Exception as e:
                logger.error("Rasm yuborishda xatolik: %s", e)
                bot.send_message(
                    user_id,
                    "⚠️ Rasmni generatsiya qilishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring yoki boshqa so'rov kiriting.",
                    reply_markup=get_main_keyboard()
                )

        try:
            threading.Thread(target=run_image_generation, daemon=True).start()
        except Exception as e:
            logger.error("Failed to start image generation thread: %s", e)
            bot.send_message(user_id, "⚠️ Rasm yaratish jarayoni boshlanmadi. Keyinroq urinib ko'ring.", reply_markup=get_main_keyboard())
        return

    # 2. Video yaratish kutilayotgan bo'lsa
    if state.get("state") == "waiting_video_prompt":
        clear_user_state(user_id)
        style = state.get("style", "cinematic")
        
        status_msg = bot.send_message(
            user_id,
            "🎬 <b>AI Video rejissyor ish boshladi...</b>\n<i>Kadrlar yaratilib, kinematik video montaj qilinmoqda (10-20 soniya olishi mumkin)...</i> ⏳",
            parse_mode="HTML"
        )
        bot.send_chat_action(user_id, "upload_video")

        def run_video_generation():
            try:
                video_file_path = generate_ai_video(user_text, style_key=style)
                caption = f"🎬 <b>Sizning AI videoroligingiz tayyor!</b>\n\n📝 <i>G'oya:</i> {html.escape(user_text)}"
                with open(video_file_path, "rb") as vf:
                    bot.send_video(
                        user_id,
                        video=vf,
                        caption=caption,
                        parse_mode="HTML",
                        supports_streaming=True,
                        reply_markup=get_main_keyboard()
                    )
                try:
                    bot.delete_message(user_id, status_msg.message_id)
                except Exception:
                    pass
                # Faylni tozalash
                try:
                    os.unlink(video_file_path)
                except Exception:
                    pass
            except Exception as e:
                logger.error("Video yaratishda xatolik: %s", e)
                bot.send_message(
                    user_id,
                    "⚠️ Video yaratishda qiyinchilik bo'ldi. Boshqa mavzuni sinab ko'ring yoki rasm chizish imkoniyatidan foydalaning.",
                    reply_markup=get_main_keyboard()
                )

        threading.Thread(target=run_video_generation).start()
        return

    # 3. AI bilan to'g'ridan-to'g'ri suhbat
    bot.send_chat_action(user_id, "typing")
    
    def run_chat_reply():
        try:
            ai_reply = ask_ai_chat(user_id, user_text)
            bot.send_message(
                user_id,
                ai_reply,
                reply_markup=get_chat_actions_keyboard()
            )
        except Exception as e:
            logger.error("Suhbatda xatolik: %s", e)
            bot.send_message(
                user_id,
                "Kechirasiz, javob tayyorlashda uzilish bo'ldi. Qayta yozib ko'ring yoki /clear qiling.",
                reply_markup=get_main_keyboard()
            )

    threading.Thread(target=run_chat_reply).start()


# ==========================================
# ASOSIY ISHGA TUSHIRISH (RUNNER)
# ==========================================

def start_bot():
    print("=" * 60)
    print("🚀 AI Telegram Bot muvaffaqiyatli ishga tushirilmoqda...")
    print("🤖 Suhbatdosh AI, Rasm, Video va Zerikmaslik funksiyalari faol!")
    print("=" * 60)

    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=20)
        except Exception as e:
            logger.critical("Bot polling jarayonida xatolik: %s. 5 soniyadan keyin qayta ishga tushadi...", e)
            time.sleep(5)


if __name__ == "__main__":
    start_bot()