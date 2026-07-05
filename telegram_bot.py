import logging
from telethon import TelegramClient, events
from os import getenv
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()
api_id = getenv("API_ID")
api_hash = getenv("API_HASH")
bot_token = getenv("BOT_TOKEN")

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Hello! Begin by sending an image to be processed by the ocr')
    logging.info(f'Start command received from {event.sender_id}')

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    help_text = ("Hi :) Send images here to have it uploaded to an OCR tool, which scans for text present in the image and adds it to a specified Obisidan vault")
    await event.respond(help_text)
    logging.info(f'Help command received from {event.sender_id}')

client.start()
client.run_until_disconnected()