import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv
from database import init_db, add_user, user_exists, get_referral_count, get_all_user_ids
from aiogram.utils.exceptions import NetworkError

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

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    # Check for referral information
    referral_id = None
    if len(message.text.split()) > 1:
        referral_id = message.text.split()[1]

    if not user_exists(user_id):
        add_user(user_id, full_name, username, referred_by=referral_id)
        if ADMIN_CHAT_ID:
            await bot.send_message(ADMIN_CHAT_ID, f"New user started the bot: {full_name} (@{username})")

    referral_link = f"https://t.me/Beckzodiy_Bot?start={user_id}"
    await message.reply(f"Hi! I'm your bot!\nInvite others using this link: {referral_link}")

@dp.message_handler(commands=['get_chat_id'])
async def get_chat_id(message: types.Message):
    await message.reply(f"Your chat ID is: {message.chat.id}")

@dp.message_handler(commands=['referrals'])
async def show_referrals(message: types.Message):
    user_id = message.from_user.id
    referral_count = get_referral_count(user_id)
    if referral_count > 0:
        await message.reply(f"You have referred {referral_count} users.")
    else:
        await message.reply(f"You haven't referred any users yet. Invite others using your referral link!\nhttps://t.me/Beckzodiy_Bot?start={user_id}")

@dp.message_handler(commands=['broadcast'])
async def broadcast_message(message: types.Message):
    if str(message.from_user.id) != ADMIN_CHAT_ID:
        await message.reply("You are not authorized to use this command.")
        return

    text = message.get_args()
    if not text:
        await message.reply("Please provide a message to broadcast.")
        return

    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text)
            logging.info(f"Sent message to {user_id}")
        except Exception as e:
            logging.error(f"Failed to send message to {user_id}: {e}")
            await message.reply(f"Failed to send message to {user_id}")

    await message.reply(f"Message sent to all {len(user_ids)} users.")
    logging.info("Broadcast message sent to all users.")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

async def on_startup(dp):
    logging.info("Bot is starting...")

async def on_shutdown(dp):
    logging.info("Bot is shutting down...W")

@dp.errors_handler(exception=NetworkError)
async def network_error_handler(update, exception):
    logging.error(f"NetworkError: {exception}")
    return True  # Suppress the exception

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
