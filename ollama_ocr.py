#TODO Handle preprocessing in separate file


from os import getenv
from dotenv import load_dotenv
from ollama import AsyncClient, ResponseError
from img_process import convert_img_to_bytes

load_dotenv()
ai_endpoint = getenv("AI_ENDPOINT")
ai_model = getenv("AI_MODEL")

client = AsyncClient(
    host=ai_endpoint
)

def model_info():
    return {
        "model": ai_model,
        "endpoint": ai_endpoint
    }

async def process_image(tg_client, chat_id, msg_id):
    img_buf = await convert_img_to_bytes(tg_client, chat_id, msg_id)
    try:
        await client.chat(ai_model)
    except ResponseError as e:
        return f"Error: {e}"

    try:
        response = await client.chat(model=ai_model, messages=[
        {
            "role": "user",
            "content": f"Could you please return the extracted text in this image and nothing else. If it is not easily human readable or humans cannot easily tell what it is, please format it in a way that it is, without adding extra content not present in the original image.",
            "images": [img_buf.getvalue()] # Can be URL or bytes
            #TODO Add content
        }])
        return response.message.content
    except ResponseError as e:
        return f"Error: {e}"



# if __name__ == "__main__":
