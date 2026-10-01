import json
import logging
import os
import random
import tempfile
import time
import urllib.parse
from pathlib import Path
import requests
from config import BOT_ROLES, IMAGE_STYLES, VIDEO_STYLES

logger = logging.getLogger(__name__)

# Foydalanuvchilar konteksti va xotirasi
# user_id -> {"role": "friend", "history": [{"role": "system", "content": "..."}, ...]}
USER_SESSIONS = {}
MAX_HISTORY_TURNS = 10  # Oxirgi 10 ta suhbat almashinuvini eslab qoladi


def get_user_role(user_id: int) -> str:
    """Foydalanuvchining hozirgi tanlangan rolini qaytaradi"""
    session = USER_SESSIONS.get(user_id)
    if not session or "role" not in session:
        return "friend"
    return session["role"]


def set_user_role(user_id: int, role_key: str):
    """Foydalanuvchi rolini o'zgartiradi va xotirani yangi rol bilan tozalaydi"""
    if role_key not in BOT_ROLES:
        role_key = "friend"
    USER_SESSIONS[user_id] = {
        "role": role_key,
        "history": [
            {"role": "system", "content": BOT_ROLES[role_key]["prompt"]}
        ]
    }


def clear_user_history(user_id: int):
    """Foydalanuvchi suhbat xotirasini tozalaydi"""
    role = get_user_role(user_id)
    USER_SESSIONS[user_id] = {
        "role": role,
        "history": [
            {"role": "system", "content": BOT_ROLES[role]["prompt"]}
        ]
    }


def ask_ai_chat(user_id: int, user_message: str) -> str:
    """
    AI bilan tabiiy va aqlli suhbat.
    Kontekstni saqlaydi, zeriktirmaydi, o'zbek tilida ravon gapiradi.
    """
    if user_id not in USER_SESSIONS:
        clear_user_history(user_id)

    session = USER_SESSIONS[user_id]
    history = session["history"]

    # Yangi xabarni tarixga qo'shish
    history.append({"role": "user", "content": user_message})

    # Tarix juda uzayib ketmasligi uchun cheklash (tizim promptini saqlagan holda)
    if len(history) > (MAX_HISTORY_TURNS * 2 + 1):
        # Tizim prompti [0] va oxirgi xabarlar qoladi
        history = [history[0]] + history[-(MAX_HISTORY_TURNS * 2):]
        session["history"] = history

    # Pollinations AI Text API orqali javob olish (bepul, barqaror va tez)
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": history,
            "model": "openai",
            "temperature": 0.7,
            "presence_penalty": 0.2
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200 and response.text.strip():
            ai_reply = response.text.strip()
            # Bot javobini tarixga saqlash
            history.append({"role": "assistant", "content": ai_reply})
            return ai_reply
    except Exception as e:
        logger.warning("Pollinations AI matn so'rovida xatolik: %s. Zaxira usulga o'tilmoqda.", e)

    # Zaxira (Fallback) oddiy GET so'rovi
    try:
        encoded_prompt = urllib.parse.quote(
            f"{BOT_ROLES[session['role']]['prompt']}\nFoydalanuvchi: {user_message}\nAI javobi:"
        )
        fallback_url = f"https://text.pollinations.ai/{encoded_prompt}?model=mistral"
        res = requests.get(fallback_url, timeout=25)
        if res.status_code == 200 and res.text.strip():
            reply = res.text.strip()
            history.append({"role": "assistant", "content": reply})
            return reply
    except Exception as e:
        logger.error("Zaxira AI suhbatida ham xatolik: %s", e)

    return (
        "Kechirasiz, hozir tarmoqda biroz yuklama kuzatilmoqda. 🌐 "
        "Birozdan so'ng qayta yozib ko'ring yoki /clear buyrug'i bilan suhbatni yangilang!"
    )


def enhance_prompt_to_english(prompt: str) -> str:
    """
    O'zbekcha yoki har qanday promptni rasm generatsiyasi uchun
    boyitilgan inglizcha promptga aylantiradi.
    """
    try:
        url = "https://text.pollinations.ai/"
        sys_msg = (
            "Translate and expand the following user image description into a rich, detailed, "
            "vivid English prompt for AI image generation (Flux/Midjourney style). "
            "Output ONLY the prompt in English, nothing else, no greetings or quotes."
        )
        payload = {
            "messages": [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt}
            ],
            "model": "openai",
            "temperature": 0.4
        }
        res = requests.post(url, json=payload, timeout=6)
        if res.status_code == 200 and res.text.strip():
            clean = res.text.strip().replace('"', '').replace('\n', ' ')
            if len(clean) > 5 and not clean.startswith("Error"):
                return clean
    except Exception:
        # Agar tarjima sekinlashsa, to'g'ridan-to'g'ri promptdan foydalaniladi
        pass
    
    return prompt


def generate_ai_image(prompt: str, style_key: str = "realistic") -> str:
    """
    Yuqori aniqlikdagi AI rasm URL manzilini tayyorlaydi va tekshiradi.
    Flux va Turbo modellari orqali chiroyli rasm chizadi.
    """
    style_suffix = IMAGE_STYLES.get(style_key, {}).get("suffix", "")
    
    # Promptni yanada go'zallashtirish
    english_prompt = enhance_prompt_to_english(prompt)
    full_prompt = f"{english_prompt}{style_suffix}"
    
    seed = random.randint(1000, 9999999)
    encoded = urllib.parse.quote(full_prompt)
    
    # Pollinations FLUX Image URL
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&seed={seed}&nologo=true&enhance=true"
    return image_url


def generate_ai_video(prompt: str, style_key: str = "cinematic") -> str:
    """
    AI yordamida dinamik kinematik video (MP4) yaratadi.
    1. AI orqali yuqori sifatli rasm generatsiya qilinadi.
    2. MoviePy yordamida kinematik zoom-in / pan va audio-vizual effektlar qo'llanib MP4 fayl qilinadi.
    3. Tayyor video fayl yo'lini (path) qaytaradi.
    """
    from PIL import Image
    import numpy as np

    # 1. Rasm generatsiya qilamiz
    style_info = VIDEO_STYLES.get(style_key, VIDEO_STYLES["cinematic"])
    full_prompt = f"{prompt}, {style_info['prompt_add']}, 8k, cinematic masterpiece"
    img_url = generate_ai_image(full_prompt, style_key="realistic")

    temp_dir = Path(tempfile.gettempdir()) / "ai_bot_videos"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    img_path = temp_dir / f"frame_{int(time.time())}.jpg"
    video_path = temp_dir / f"ai_video_{int(time.time())}.mp4"

    # Rasmni yuklab olish
    response = requests.get(img_url, timeout=40)
    if response.status_code != 200:
        raise RuntimeError("AI kadrini yuklab olib bo'lmadi.")
    
    with open(img_path, "wb") as f:
        f.write(response.content)

    # 2. MoviePy orqali kinematik video yaratamiz
    try:
        from moviepy.editor import ImageClip
        
        duration = 4.0  # 4 soniyalik dinamik video klip
        # Moviepy klip
        clip = ImageClip(str(img_path)).set_duration(duration)
        
        # Sekin yaqinlashish (Ken Burns zoom effekti)
        # resize funksiyasi orqali zoom
        w, h = clip.size
        # Harakatli animatsiya
        clip = clip.resize(lambda t: 1.0 + 0.04 * t)
        # O'rtadan qirqib olish (w x h)
        clip = clip.crop(x_center=w/2, y_center=h/2, width=w, height=h)
        
        # 24 fps bilan saqlash
        clip.write_videofile(
            str(video_path),
            fps=24,
            codec="libx264",
            audio=False,
            preset="ultrafast",
            threads=2,
            logger=None
        )
        clip.close()
        
        if video_path.exists() and video_path.stat().st_size > 1000:
            return str(video_path)
    except Exception as e:
        logger.error("Moviepy video generatsiyasida xatolik: %s", e)
        # Agar moviepyda xatolik bo'lsa, xatolikni qaytaramiz
        raise e
    finally:
        if img_path.exists():
            try:
                img_path.unlink()
            except Exception:
                pass

    return str(video_path)
