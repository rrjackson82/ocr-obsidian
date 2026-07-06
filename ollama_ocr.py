from ollama import AsyncClient, ResponseError
from img_process import convert_img_to_bytes
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
            "content": f"You are an expert in transcribing images to markdown. Could you please return the extracted text in this image and nothing else. If it is not easily human readable or humans cannot easily tell what it is, please format it in a way that it is, without adding extra content not present in the original image. Format as markdown to make it look similar to the original image. Headers, lists, bullet points, etc seen in the image should be reflected in the markdown.",
            "images": [img_buf.getvalue()] # Can be URL or bytes
        }], options={"temperature": settings.ai_temp})
        return response.message.content
    except ResponseError as e:
        return f"Error: {e}"



# if __name__ == "__main__":
