import logging

from ollama import ResponseError
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
    await event.respond('Hello! Begin by sending an image to be processed by the ocr or type /help for available commands')
    logging.info(f'Start command received from {event.sender_id}')

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    user_state[event.sender_id] = {
        "step": "help"
    }
    help_text = ("""Hi :) Send images here to have it uploaded to an OCR tool, which scans for text in the image, converts it to markdown, and adds it to a chosen Obsidian vault

/help: This command
/settings: Tweak settings such as the AI model, AI endpoints, creating new vaults, and adding existing vaults
/list: list all registered vaults.""")
    await event.respond(help_text)
    logging.info(f'Help command received from {event.sender_id}')

@client.on(events.NewMessage(pattern="/settings"))
async def settings(event):
    buttons = [Button.inline("Change Model", b"Change Model"), Button.inline("Change Endpoint", b"Change Endpoint"),
               Button.inline("Create New Vault", b"Create Vault"), Button.inline("Add Existing Vault", b"Add Vault")]
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
    await event.respond(f"Step 1) Generating metadata from image using {model_info()['model']}, this may take some time...")

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

    # after user clicks the settings button
    if state["step"] == "settings" and state["function"] != "":
        match state["function"]:
            case "change_model":
                await event.respond(f"Setting model to {text}...")
                obsidian.settings.ai_model = text
                obsidian.settings.save()
                await event.respond(f"Done! Set model to {text}.")
            case "change_endpoint":
                await event.respond(f"Changing Ollama endpoint to {text}...")
                obsidian.settings.ai_endpoint = text
                obsidian.settings.save()
                await event.respond(f"Done! Set model to {text}.")
            case "create_vault":
                name = text
                obsidian.settings.create_vault(name)
                vault = obsidian.settings.get_vault(name)
                await event.respond(f"Created vault '{name}' at path '{vault.path}'")
            case "add_vault":
                print("hello from add_vault")
                await event.respond(f"Adding vault '{text}'...")
                try:
                    obsidian.settings.add_vault(text)
                    await event.respond("Added vault!")
                except ValueError:
                    await event.respond(f"Vault '{text}' already exists!")

@client.on(events.CallbackQuery)
async def handle_button(event):
    data = event.data #returns bytes
    state = user_state.get(event.sender_id)
    await event.answer()
    if state["step"] == "ask_obsidian_vault":
        # generate tags, title, file name, etc
        vault_name = data.decode()
        vault = obsidian.settings.get_vault(vault_name)

        await event.respond(f"Generating file data (title, filename, etc). This may take some time...")
        try:
            metadata = await obsidian.generate_file_data(vault, state["markdown"])
            await event.respond("Adding to Vault...")
            obsidian.create_note(vault, state["markdown"], metadata['filename'], metadata['tags'])
            await event.respond(f"Created note {metadata['filename']}.md to vault '{vault_name}'")
        except ResponseError:
            await event.respond("Ollama error - Check your endpoint, model, and make sure it's connected")

    elif state["step"] == "settings":
        # change model, change endpoint, add vault
        match data.decode().strip().lower():
            case "change model":
                await event.respond(f"""Ok, let's change the model.
Please type in the exact model name.
 For example, Type 'qwen2.5vl:3b' for the 'qwen2.5vl:3b' model.
This should be the same thing you type to download models with ollama:
```ollama run <model-name>``` or ```ollama pull <model name>```
For a list of all models installed on your machine, run ```ollama list``` in your terminal.
Make sure you have the model actually installed!
You are currently using {obsidian.settings.ai_model}
Which model would you like to change to?""")
                user_state[event.sender_id] = {
                    "step": "settings",
                    "function": "change_model"
                }


            case "change endpoint":
                await event.respond(f"""You selected to change the endpoint. 
You are currently using
```{obsidian.settings.ai_endpoint}```

Ollama's default is 
```http://localhost:11434```

Your endpoint should start with 'http://' or 'https://'. An example would be:
```http://123.45.678.90:11434```

Please type the endpoint you'd like to use. 
""")
                user_state[event.sender_id] = {
                    "step": "settings",
                    "function": "change_endpoint"
                }


            case "create vault":
                vaults = ""
                for vault in obsidian.settings.list_vaults():
                    name = vault[0]
                    vaults = vaults + "    __" + name + "__\n"
                await event.respond(f"""You selected to add a vault.
Your current vaults are:
{vaults}
""")
                await event.respond("What would you like to name your vault? This will be the folder name.")
                user_state[event.sender_id] = {
                    "step": "settings",
                    "function": "create_vault",
                }
            case "add vault":
                await event.respond(f"You selected to add an existing vault. When you input a name, it scans your base folder for any vault by that name.")
                user_state[event.sender_id] = {
                    "step": "settings",
                    "function": "add_vault"
                }



client.start()
client.run_until_disconnected()