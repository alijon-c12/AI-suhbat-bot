# 🌟 Super AI Telegram Bot - Brending va Ishga Tushirish Qo'llanmasi

Ushbu qo'llanmada botingiz uchun eng zo'r nomlar, esda qolarli username variantlari, BotFather sozlamalari va botni ishga tushirish yo'riqnomasi keltirilgan.

---

## 1. 🏷️ Bot Uchun Eng Zo'r Nomlar (Bot Name)
BotFather-da `/setname` orqali quyidagi chiroyli nomlardan birini tanlashingiz mumkin:

1. **Lumos AI | Aqlli Hamroh 🌟** *(Tavsiya qilinadi - zamonaviy va jarangdor)*
2. **Nova AI — Sizning Aqlli Do'stingiz 🤖**
3. **Zehn AI | Suhbat, Rasm & Video ✨**
4. **Aura AI | Aqlli Yordamchi & Do'st 🧠**
5. **Orion AI — Universal Hamroh 🚀**

---

## 2. 💎 Zo'r Username Variantlari (Bot Username)
Telegramda bot yaratishda yoki `/setusername` qilishda quyidagi variantlarni tekshirib ko'ring (yoki o'zingizga mos brend qo'shing):

- `@LumosUzBot` yoki `@LumosAIBot`
- `@NovaMindUzBot` yoki `@NovaSmartBot`
- `@ZehnUzBot` yoki `@ZehnAIBot`
- `@AuraSuperBot` yoki `@AuraMindBot`
- `@SmartHamrohBot`
- `@InnoAIBot`

*(Eslatma: Telegramda bot username oxiri albatta `bot` yoki `Bot` bilan tugashi kerak).*

---

## 3. 📝 BotFather Tavsiflari (Description & About)

### A) `/setdescription` (Foydalanuvchi birinchi marta botga kirganda ko'rinadigan matn):
```text
Assalomu alaykum! Men sizning universal AI hamrohingizman 🤖✨

Imkoniyatlarim:
💬 Siz bilan qiziqarli va do'stona suhbat quraman
🎨 Har qanday tasavvuringizni yuqori sifatli rasmga aylantiraman (Flux HD)
🎬 Siz uchun kinematik video roliklar yasab beraman
🎭 Qiyofamni o'zgartira olaman (Do'st, Psixolog, Dasturchi, Qiziqchi)
🎮 Zerikmaslik uchun viktorina, latifa va qiziqarli o'yinlar taqdim etaman

Boshlash uchun pastdagi "Start" tugmasini bosing! 👇
```

### B) `/setabouttext` (Bot profili haqida qisqa ma'lumot):
```text
🌟 Sizning aqlli, quvnoq va universal AI hamrohingiz. Suhbat, rasm, video va yordam — barchasi bir joyda!
```

---

## 4. ⚡ BotFather Buyruqlari (`/setcommands`)
BotFather-ga `/setcommands` yuboring va quyidagi ro'yxatni nusxalab jo'nating:

```text
start - Botni ishga tushirish va asosiy menyu
chat - AI bilan do'stona suhbat boshlash
image - AI orqali yuqori sifatli rasm chizish
video - AI orqali kinematik video yaratish
roles - Bot xarakterini o'zgartirish (Do'st, Psixolog, Dasturchi...)
clear - Suhbat xotirasini tozalash (yangi mavzu)
help - Yordam va imkoniyatlar qo'llanmasi
```

---

## 5. 🚀 Botni Qanday Ishga Tushirasiz?

### 1-qadam: Tokenni kiritish
Loyiha papkasidagi `.env` faylini oching va Telegram bot tokeningizni yozing:
```env
TELEGRAM_BOT_TOKEN=7777777777:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2-qadam: Botni ishga tushirish
Terminalda (yoki VS Code / PyCharm terminalida) quyidagi buyruqni bering:
```bash
python main.py
```

### 3-qadam: Telegramda sinab ko'ring!
Telegramda botingizga kiring va `/start` yuboring. Barcha boy menyular, rasm chizish, video yaratish va AI do'st xizmatda bo'ladi! 🎉
