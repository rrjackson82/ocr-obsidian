# TODO add commands for obsidian vault scanning and viewing, available tags, AI endpoints etc


import logging
from telethon import TelegramClient, events, utils
from os import getenv
from dotenv import load_dotenv
from tesseract_ocr import ocr_image_from_telethon

logging.basicConfig(level=logging.INFO)

load_dotenv()
api_id = getenv("API_ID")
api_hash = getenv("API_HASH")
bot_token = getenv("BOT_TOKEN")
user_state = {}

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Hello! Begin by sending an image to be processed by the ocr')
    logging.info(f'Start command received from {event.sender_id}')

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    help_text = ("Hi :) Send images here to have it uploaded to an OCR tool, which scans for text present in the image and adds it to a specified Obisidan vault",
    "/help: This command",
    "/settings: Tweak settings such as default OCR model (under development)")
    await event.respond(help_text)
    logging.info(f'Help command received from {event.sender_id}')

@client.on(events.NewMessage(pattern="/settings"))
async def settings(event):
    await event.respond("Coming soon")

@client.on(events.NewMessage(func=lambda e: bool(e.media) and utils.is_image(e.media)))
async def handle_image(event):
    user_state[event.sender_id] = {
        "step": "ask_ocr_model",
        "chat_id": event.chat_id,
        "img_msg_id": event.id
    }
    await event.respond("""
    Image detected.
    1) OCR model selection
    Please select which OCR model (image to text engine) you would like to use
    \n\ta) Tesseract (machine learning: faster, less accurate. Easiest to start)
    \n\tb) Locally hosted AI (you host, add your own endpoint in /settings: Slower but more accurate)
    \nRespond with 'a', 'b', 'tesseract', or 'ai'
    """)
    print(f"user state: {user_state}")

@client.on(events.NewMessage)
async def handle_followup(event):
    state = user_state.get(event.sender_id)
    if not state:
        event.respond("User state err")
        return
    
    if state["step"] == "ask_ocr_model":
        answer = event.text.lower()

        if answer.lower() in ['b', 'ai']:
            await event.respond("You selected to use AI")

        elif answer.lower() in ['a', 'tesseract']:
            await event.respond("You have selected to use tesseract")
            text = await ocr_image_from_telethon(client, state["chat_id"], state["img_msg_id"])
            await event.respond(text)
        else:
            await event.respond("Response not in options")


client.start()
client.run_until_disconnected()