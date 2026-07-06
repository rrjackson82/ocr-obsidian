from fetch_settings import Settings, Vault
from ollama import AsyncClient, ResponseError
settings = Settings.load()

def search_tags(vault: Vault):
    print(f"Searching for tags in '{vault.name}'")

async def generate_file_data(content):
    return

def create_note(vault: Vault, content: str):
    print('---///---')
    print(f"Creating note '{vault.name}' in vault '{vault.name}'")
    print('---///---')