import instaloader
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Укажи свой токен
TOKEN = "7663426379:AAFR6lhEHn5EJBlAOu6KbWqVl906BF_RcsQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()
loader = instaloader.Instaloader()

# Словарь для хранения выбранного языка пользователя
user_languages = {}

# Доступные языки
LANGUAGES = {
    "🇬🇧 English": "en",
    "🇷🇺 Русский": "ru",
    "🇺🇿 Oʻzbek": "uz"
}

MESSAGES = {
    "en": {"start": "Choose your language:", "waiting": "Please wait... Downloading video.", "error": "Send a valid Instagram video link.", "humor": ["Oops! Try again!", "Hmm, what do you mean?", "I am a bot, not a mind reader! 😆"]},
    "ru": {"start": "Выберите язык:", "waiting": "Подождите... Загружаем видео.", "error": "Отправьте корректную ссылку на видео из Instagram.", "humor": ["Ой! Попробуйте снова!", "Хм, что вы имеете в виду?", "Я бот, а не телепат! 😆"]},
    "uz": {"start": "Tilni tanlang:", "waiting": "Iltimos, kuting... Video yuklanmoqda.", "error": "Instagram video havolasini yuboring.", "humor": ["Voy! Qayta urinib ko'ring!", "Hmm, nimani nazarda tutyapsiz?", "Men botman, telepat emasman! 😆"]}
}

# Клавиатура для выбора языка
lang_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(flag)] for flag in LANGUAGES],
    resize_keyboard=True
)

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # Если пользователь выбирает язык
    if text in LANGUAGES:
        user_languages[user_id] = LANGUAGES[text]
        await message.reply("✅ " + MESSAGES[user_languages[user_id]]["start"] + "\n\n" + MESSAGES[user_languages[user_id]]["error"], reply_markup=types.ReplyKeyboardRemove())
        return

    # Проверяем, выбрал ли пользователь язык
    if user_id not in user_languages:
        await message.reply(MESSAGES["en"]["start"], reply_markup=lang_keyboard)
        return

    lang = user_languages[user_id]
    
    if "instagram.com" not in text:
        await message.reply(MESSAGES[lang]["humor"][hash(text) % len(MESSAGES[lang]["humor"])] )
        return
    
    await message.reply(MESSAGES[lang]["waiting"])
    
    try:
        shortcode = text.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target="downloads")
        
        for file in os.listdir("downloads"):
            if file.endswith(".mp4") or file.endswith(".jpg"):
                file_path = os.path.join("downloads", file)
                media = types.FSInputFile(file_path)  # Используем FSInputFile
                
                if file.endswith(".mp4"):
                    await message.answer_video(media, caption="🎬 Video downloaded from Instagram!")
                else:
                    await message.answer_photo(media, caption="📷 Photo from Instagram!")
                
                os.remove(file_path)
    
    except Exception as e:
        await message.reply(f"⚠️ {MESSAGES[lang]['error']}\n({str(e)})")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
