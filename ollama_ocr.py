#TODO Handle preprocessing in separate file


from os import getenv
import asyncio
from dotenv import load_dotenv
from ollama import AsyncClient, ResponseError
from PIL import Image
from io import BytesIO

load_dotenv()
ai_endpoint = getenv("AI_ENDPOINT")
ai_model = getenv("AI_MODEL")

client = AsyncClient(
    host=ai_endpoint
)

async def process_image(url):
    try:
        await client.chat(ai_model)
    except ResponseError as e:
        return f"Error: {e}"

    try:
        response = await client.chat(model=ai_model, messages=[
        {
            "role": "user",
            "content": f"Could you please return the extracted text in this image and nothing else",
            "images": [url]
            #TODO Add content
        }])
        return response.message.content
    except ResponseError as e:
        return f"Error: {e}"


async def main():
    content = await process_image("example-text.png")
    print(content)

if __name__ == "__main__":
    asyncio.run(main())