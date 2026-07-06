from fetch_settings import Settings, Vault

settings = Settings.load()
def get_def():
    print(settings.default_vault)

def search_tags(vault: Vault):
    print(f"Searching for tags in '{vault.name}'")

get_def()