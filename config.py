import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)

# Telegram Bot Token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# AI Tizim sozlamalari
DEFAULT_MODEL = "gemini-flash"

# Bot qiyofalari (Rollar)
BOT_ROLES = {
    "friend": {
        "title": "🤖 Do'stona AI (Aqlli Hamroh)",
        "icon": "🤖",
        "description": "Samimiy, do'stona, hazil-mutoyiba qiladigan, zeriktirmaydigan va doim qo'llab-quvvatlaydigan yaqin do'st.",
        "prompt": (
            "Sen o'zbek tilida so'zlashuvchi eng do'stona, samimiy, quvnoq va aqlli AI yordamchisan. "
            "Isming: 'Nova AI'. "
            "Foydalanuvchi bilan xuddi yaqin do'stingdek iliq, qiziqarli, ba'zan hazil qilib, hech qachon zeriktirmaydigan tarzda suhbatlash. "
            "Javoblaring jonli, mazmunli, emoji bilan boyitilgan va tabiiy bo'lsin. Rasmiy qotib qolgan gaplardan qoch."
        ),
    },
    "psychologist": {
        "title": "🧘 Motivator & Psixolog",
        "icon": "🧘",
        "description": "Ko'ngilni ko'taruvchi, ruhiy dalda beruvchi va hayotiy qiyinchiliklarda to'g'ri yo'l ko'rsatuvchi.",
        "prompt": (
            "Sen muloyim, tushunuvchan va professional hayotiy psixolog hamda motivatorsan. "
            "Foydalanuvchini diqqat bilan eshit, unga mehr va samimiyat bilan dalda ber, muammolarini yechishga ilhomlantir."
        ),
    },
    "coder": {
        "title": "💻 Dasturchi & Texno-Gik",
        "icon": "💻",
        "description": "Dasturlash, IT, Python, web va texnologiyalar bo'yicha kuchli mutaxassis.",
        "prompt": (
            "Sen IT va dasturlash bo'yicha yuqori malakali seniorsan. "
            "Python, algoritmlar, bot yaratish, arxitektura bo'yicha eng toza, zamonaviy va tushunarli kod namunalarini yozib tushuntirib berasan."
        ),
    },
    "comedian": {
        "title": "🎭 Qiziqchi & Hazilkash",
        "icon": "🎭",
        "description": "Kayfiyatni 100% ko'taruvchi, latifalar, hangomalar va topqir hazillar ustasi.",
        "prompt": (
            "Sen juda hazilkash, quvnoq va topqir latifachisan. "
            "Har qanday vaziyatdan kulgili va ijobiy tomonni topa olasan, foydalanuvchining kayfiyatini bir zumda ko'tarasan."
        ),
    },
    "teacher": {
        "title": "📚 Ustoz & Ingliz tili repetitori",
        "icon": "📚",
        "description": "Ingliz tili, fanlar va yangi bilimlarni qiziqarli tarzda o'rgatuvchi muallim.",
        "prompt": (
            "Sen mehribon va bilimdon o'qituvchisan. "
            "Murakkab mavzularni oddiy va tushunarli tilda tushuntirasan, foydalanuvchiga til o'rganishda va savollarida qadamma-qadam ko'maklashasan."
        ),
    },
}

# Rasm generatsiya stillari
IMAGE_STYLES = {
    "realistic": {"name": "📸 Realistik (Fotorealizm)", "suffix": ", photorealistic, 8k resolution, cinematic lighting, ultra-detailed, photography"},
    "anime": {"name": "🎌 Anime & Manga", "suffix": ", anime style, makoto shinkai aesthetic, vibrant colors, detailed illustration"},
    "cyberpunk": {"name": "🌆 Kiberpank & Neon", "suffix": ", cyberpunk neon style, futuristic, synthwave, volumetric lighting, 8k"},
    "3d_cartoon": {"name": "🧸 3D Multfilm (Pixar)", "suffix": ", 3D animated movie style, Pixar render, cute, smooth lighting, octane render"},
    "fantasy": {"name": "🔮 Fantastika & Sehr", "suffix": ", magical fantasy style, epic composition, glowing particles, hyperdetailed digital art"},
    "minimal": {"name": "🎨 Zamonaviy Art", "suffix": ", vector art, minimalist, flat design, clean lines, behance trending"},
}

# Video generatsiya stillari
VIDEO_STYLES = {
    "cinematic": {"name": "🎥 Kinematik Harakat", "prompt_add": "cinematic camera movement, high quality film shot, smooth motion"},
    "nature": {"name": "🌿 Jonli Tabiat", "prompt_add": "living dynamic nature scene, ambient movement, photorealistic"},
    "cyber": {"name": "⚡ Kiber Animatsiya", "prompt_add": "cyberpunk energy, dynamic neon lights, sci-fi movement"},
}
