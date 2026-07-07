import fetch_settings
from ollama_handler import text_prompt
from pathlib import Path
import subprocess

settings = fetch_settings.Settings.load()

def search_tags(vault: fetch_settings.Vault):
    path = Path(vault.path)

    print(f"Searching for tags in '{vault.name}'")
    result = subprocess.run(
        ["grep", "-rh", "--include=*.md", "-o", r"#\w\+", path],
        capture_output=True, text=True
    )
    tags = list(set(result.stdout.splitlines()))

    # for file in path.rglob(f"{path}/**/*.md"):
    #     with open(file, "r") as f:
    #         file_content = f.read()

    vault.tags = tags
    return tags

async def generate_file_data(vault: fetch_settings.Vault, content):
    prompt = f"""Take the following file and add the following file-data:
    -File name
    -Tags
    Rules:
    -File name should be relevant to the content on the page
    -Do not include file extensions in file name-give name only
    -Do not include dots (.) in filename. Replace spaces with hyphen (-)
    -Do not edit the content in any way
    -Only add tags if it is necessary
    -Create a tag only if the options in the 'tags' section do not suffice 
    -If you create a tag, switch 'createdTag' to True. Otherwise leave False
    
    Tags list:
    {vault.tags}
    
    File:
    ---
    {content}
    ---
    
    Format the result in this format:
    
    {{
        "filename": str,
        "tags": [str],
        "createdTag" bool
    }}
    
    """
    data = text_prompt(prompt)
    filename = data["filename"]
    tags = data["tags"]
    createdTag = data["createdTag"]

    if createdTag:
        search_tags(vault)
    return

def create_note(vault: fetch_settings.Vault, content: str):
    print('---///---')
    print(f"Creating note '{vault.name}' in vault '{vault.name}'")
    print('---///---')

if __name__ == '__main__':
    vault = settings.get_vault(settings.default_vault)
    print(search_tags(vault))
    print("saving...")
    settings.save()
    print("done")
