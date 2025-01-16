import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web
from dotenv import load_dotenv
from database import init_db, add_user, user_exists

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Initialize the database
init_db()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    if not user_exists(user_id):
        add_user(user_id, full_name, username)
        if ADMIN_CHAT_ID:
            await bot.send_message(ADMIN_CHAT_ID, f"New user started the bot: {full_name} (@{username})")

    await message.reply("Hi!\nI'm your bot!\nPowered by aiogram.")

@dp.message_handler(commands=['get_chat_id'])
async def get_chat_id(message: types.Message):
    await message.reply(f"Your chat ID is: {message.chat.id}")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

async def on_startup(app):
    webhook_url = os.getenv('WEBHOOK_URL')
    await bot.set_webhook(webhook_url)

app = get_new_configured_app(dispatcher=dp, path='/')
app.on_startup.append(on_startup)

if __name__ == '__main__':
    web.run_app(app, port=int(os.getenv('PORT', 3000)))
