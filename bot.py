import instaloader
import os
import asyncio
from aiogram import Bot, Dispatcher, types

# Укажи свой токен
TOKEN = "7663426379:AAFR6lhEHn5EJBlAOu6KbWqVl906BF_RcsQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()
loader = instaloader.Instaloader()

@dp.message()
async def handle_message(message: types.Message):
    url = message.text
    if "instagram.com" not in url:
        await message.reply("Ey do‘stim! Instagram'dan video yuklab olish uchun to‘g‘ri havolani yubor, bo‘lmasa, men hech narsa qila olmayman! 🚀 .")
        return
    
    try:
        shortcode = url.split("/")[-2]
        loader.download_post(instaloader.Post.from_shortcode(loader.context, shortcode), target="downloads")
        
        for file in os.listdir("downloads"):
            if file.endswith(".mp4"):
                file_path = os.path.join("downloads", file)
                video = types.FSInputFile(file_path)  # Используем FSInputFile
                await message.answer_video(video)
                os.remove(file_path)
        
    except Exception as e:
        await message.reply(f"Ошибка при скачивании: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
