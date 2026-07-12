from datetime import datetime
import fetch_settings
from ollama_handler import text_prompt
from pathlib import Path
import subprocess
from json import loads

settings = fetch_settings.Settings.load()

def search_tags(vault: fetch_settings.Vault):
    path = Path(vault.path)

    print(f"Searching for tags in '{vault.name}'")
    result = subprocess.run(
        ["grep", "-rh", "--include=*.md", "-o", r"#\w\+", path],
        capture_output=True, text=True
    )
    tags = list(set(result.stdout.splitlines()))
    vault.tags = tags
    return tags

async def generate_file_data(vault: fetch_settings.Vault, content):
    if not vault.tags:
        search_tags(vault)
    print(f"Vault tags: {vault.tags}")
    prompt = f"""Take the following file and add the following file-data:
    -File name
    -Tags
    Rules:
    - File name should be relevant to the content on the page
    - Do not include file extensions in file name-give name only
    - Do not include dots '.' in filename. Replace spaces with '%^'
    - Filename should be in title case
    - Do not edit the content in any way
    - Only add tags if it is necessary
    - Tags must start with '#' and be all lowercase
    - Create a tag only if the options in the 'tags' section are not related to the note contents

    
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
    data = await text_prompt(prompt)
    raw = data.message.content
    raw = raw[raw.index('{'):raw.index('}')+1]
    data = loads(raw)
    filename = data["filename"]
    tags = data["tags"]
    createdTag = data["createdTag"]
    if createdTag:
        current_tags = search_tags(vault)
        total_tags = list(dict.fromkeys(current_tags + (tags or []))) # Avoid duplicates
        vault.tags = total_tags
        settings.save()
    return {
        "filename": filename.replace('%^', " "),
        "tags": tags,
    }

def create_note(vault: fetch_settings.Vault, content: str, filename: str, tags: list):
    full_path = Path(vault.path) / f"{filename}.md"
    if tags:
        formatted_tags = f"{' '.join(tags)}"
        pre_content = f"""Tags: {formatted_tags}\nCreated: {datetime.now().date()}"""
    else:
        pre_content = f"Created: {datetime.now().date()}"
    final_content = f"""{pre_content}\n{content}"""

    full_path.write_text(final_content)

if __name__ == '__main__':
    vault = settings.get_vault(settings.default_vault)
    print(search_tags(vault))
    print("saving...")
    settings.save()
    print("done")
