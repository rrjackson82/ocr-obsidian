# TODO add commands for obsidian vault scanning and viewing, available tags, AI endpoints etc

import logging
from urllib.parse import uses_relative

from telethon import TelegramClient, events, utils, Button
from os import getenv
from dotenv import load_dotenv
import obsidian
from ollama_ocr import model_info, process_image
from fetch_settings import Settings

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
    buttons = [Button.inline("Change Model", b"Change Model"), Button.inline("Change Endpoint", b"Change Endpoint"),
               Button.inline("Add Vault", b"Add Vault")]
    user_state[event.sender_id] = {
        "step": "settings",
        "function": ""
    }
    await event.respond("What would you like to do?", buttons=buttons)

@client.on(events.NewMessage(pattern="/list"))
async def list_vaults(event):
    vaults = list_vaults()
    await event.respond(f"Your registered vaults:\n{vaults}")

## WHEN USER SENDS IMAGE
@client.on(events.NewMessage(func=lambda e: bool(e.media) and utils.is_image(e.media)))
async def handle_image(event):
    user_state[event.sender_id] = {
        "step": "generate_metadata",
        "chat_id": event.chat_id,
        "img_msg_id": event.id
    }
    state = user_state.get(event.sender_id)
    await event.respond(f"Step 1) Generating metadata from image using {model_info()['model']}, this may take some time")

    #generate metadata
    response = await process_image(client, state["chat_id"], state["img_msg_id"])
    # await event.respond(response)
    await event.respond("Generated markdown from image.")
    user_state[event.sender_id] = {
        "step": "ask_obsidian_vault",
        "markdown": response,
    }

    # choosing obsidian vault
    buttons = []
    usr_vaults = Settings.load().vaults
    for vault in usr_vaults:
        buttons.append(Button.inline(vault.name, f"{vault.name}".encode()))
    await event.respond("Step 2) Vault selection", buttons=buttons)

@client.on(events.NewMessage)
async def handle_followup(event):
    state = user_state.get(event.sender_id)
    text = event.text
    if not state:
        await event.respond("User state err")
        return

    # after user clicks the button
    if state["step"] == "settings" and state["function"] != "":
        match state["function"]:
            case "change_model":
                await event.respond(f"Setting model to {text}")
                obsidian.settings.ai_model = text
                obsidian.settings.save()
                await event.respond(f"Done! Set model to {text}")
            case "change_model":
                return
            case "change_endpoint":
                return
            case "add_vault":
                return


@client.on(events.CallbackQuery)
async def handle_button(event):
    data = event.data #returns bytes
    state = user_state.get(event.sender_id)
    await event.answer()
    if state["step"] == "ask_obsidian_vault":
        # generate tags, title, file name, etc
        vault_name = data.decode()
        vault = obsidian.settings.get_vault(vault_name)

        await event.respond(f"Selected '{vault_name}', generating file data (title, filename, etc)")
        metadata = await obsidian.generate_file_data(vault, state["markdown"])
        await event.respond("Adding to Vault...")
        obsidian.create_note(vault, state["markdown"], metadata['filename'], metadata['tags'])
        await event.respond(f"Created note {metadata['filename']}.md to vault '{vault_name}'")
    elif state["step"] == "settings":
        # change model, change endpoint, add vault
        match data.decode().strip().lower():
            case "change model":
                await event.respond(f"""Ok, let's change the model.

Please type in the exact model name.
 
For example: Type 'qwen2.5vl:3b' for the 'qwen2.5vl:3b' model.
This should be the same thing you type to download models with ollama:
```ollama run <model-name>``` or ```ollama pull <model name>```

For a list of all models, run ```ollama list```

You are currently using {obsidian.settings.ai_model}""")
                user_state[event.sender_id] = {
                    "step": "settings",
                    "function": "change_model"
                }
            case "change endpoint":
                await event.respond(f"You selected to change the endpoint")
                user_state[event.sender_id] = {
                    "step": "settings",
                    "function": "change_endpoint"
                }
            case "add vault":
                await event.respond(f"You selected to add a vault")
                user_state[event.sender_id] = {
                    "step": "settings",
                    "function": "add_vault"
                }



client.start()
client.run_until_disconnected()