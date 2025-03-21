import instaloader
import os
import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup

# Укажи свой токен
TOKEN = "7583472767:AAFQ7rXjLloMv39nSvSh-Dcl1GRN5LXxi3E"

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
    "en": {
        "start": "Choose your language:",
        "waiting": "Please wait... Downloading video.",
        "error": "Send a valid Instagram video link.",
        "private": "This post is from a private account. I can't download it.",
        "not_found": "The post was not found. It may have been deleted or the link is incorrect.",
        "blocked": "Too many requests! Instagram has temporarily blocked access. Try again later.",
        "humor": ["Oops! Try again!", "Hmm, what do you mean?", "I am a bot, not a mind reader! 😆"]
    },
    "ru": {
        "start": "Выберите язык:",
        "waiting": "Подождите... Загружаем видео.",
        "error": "Отправьте корректную ссылку на видео из Instagram.",
        "private": "Этот пост из закрытого аккаунта. Я не могу его скачать.",
        "not_found": "Пост не найден. Возможно, он был удалён или ссылка некорректна.",
        "blocked": "Слишком много запросов! Instagram временно заблокировал доступ. Попробуйте позже.",
        "humor": ["Ой! Попробуйте снова!", "Хм, что вы имеете в виду?", "Я бот, а не телепат! 😆"]
    },
    "uz": {
        "start": "Tilni tanlang:",
        "waiting": "Iltimos, kuting... Video yuklanmoqda.",
        "error": "Instagram video havolasini yuboring.",
        "private": "Bu post yopiq akkauntdan. Uni yuklab bo'lmaydi.",
        "not_found": "Post topilmadi. U o'chirilgan yoki havola noto'g'ri.",
        "blocked": "Ko'p so'rov yuborildi! Instagram vaqtincha bloklagan. Keyinroq urinib ko'ring.",
        "humor": ["Voy! Qayta urinib ko'ring!", "Hmm, nimani nazarda tutyapsiz?", "Men botman, telepat emasman! 😆"]
    }
}

# Клавиатура для выбора языка
lang_keyboard = ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text=flag)] for flag in LANGUAGES.keys()],
    resize_keyboard=True
)

# Регулярное выражение для проверки ссылки
INSTAGRAM_REGEX = re.compile(r"https?://(www\.)?instagram\.com/(p|reel|tv)/([A-Za-z0-9_-]+)")

# Функция очистки папки "downloads"
def clean_downloads():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    for file in os.listdir("downloads"):
        file_path = os.path.join("downloads", file)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении {file}: {e}")

@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.reply(MESSAGES["en"]["start"], reply_markup=lang_keyboard)

@dp.message(F.text)
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

    # Проверяем, является ли текст ссылкой на Instagram
    match = INSTAGRAM_REGEX.search(text)
    if not match:
        await message.reply(MESSAGES[lang]["humor"][hash(text) % len(MESSAGES[lang]["humor"])])
        return

    await message.reply(MESSAGES[lang]["waiting"])

    # Очищаем папку перед загрузкой
    clean_downloads()

    shortcode = match.group(3)  # Извлекаем код поста

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Проверяем, не является ли пост приватным
        if post.owner_profile.is_private:
            await message.reply(f"⚠️ {MESSAGES[lang]['private']}")
            return

        loader.download_post(post, target="downloads")

        # Отправляем видео пользователю
        for file in os.listdir("downloads"):
            if file.endswith(".mp4"):
                file_path = os.path.join("downloads", file)
                media = types.FSInputFile(file_path)  # Используем FSInputFile
                await message.answer_video(media, caption="🎬 Video downloaded from Instagram!")
                os.remove(file_path)

    except instaloader.exceptions.ProfileNotExistsException:
        await message.reply(f"⚠️ {MESSAGES[lang]['not_found']}")
    
    except instaloader.exceptions.ConnectionException:
        await message.reply(f"⚠️ {MESSAGES[lang]['blocked']}")

    except Exception as e:
        await message.reply(f"⚠️ {MESSAGES[lang]['error']}\n({str(e)})")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
