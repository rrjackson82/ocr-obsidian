from ollama import AsyncClient, ResponseError
from fetch_settings import Settings

settings = Settings.load()
ai_model = settings.ai_model
ai_endpoint = settings.ai_endpoint
client = AsyncClient(
    host=ai_endpoint
)

def model_info():
    return {
        "model": ai_model,
        "endpoint": ai_endpoint
    }

async def text_prompt(prompt):
    try:
        await client.chat(ai_model)
    except ResponseError:
        raise ResponseError("Ollama Error", 500)

    try:
        response = await client.chat(model=ai_model, messages=[
        {
            "role": "user",
            "content": prompt
        }
        ], options={"temperature": settings.ai_temp})
        return response
    except ResponseError:
        raise ResponseError("Ollama Error", 500)

async def img_prompt(prompt, img_bytes):
    try:
        await client.chat(ai_model)
    except ResponseError:
        raise ResponseError("Ollama Error", 500)

    try:
        response = await client.chat(model=ai_model, messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [img_bytes]
            }
        ], options={"temperature": settings.ai_temp})
        return response
    except ResponseError:
        raise ResponseError("Ollama Error", 500)