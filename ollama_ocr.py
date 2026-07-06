import re
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

        ocr_prompt = """Look at this image of a handwritten or printed notebook page.

        Transcribe every piece of text you see, top to bottom, left to right.

        Rules:
        - Output ONLY the raw transcribed text. No commentary, no "Here is the text:".
        - Preserve line breaks exactly as they appear in the image.
        - If text is indented or offset (like a sub-point under a main point), keep that indentation using spaces.
        - If you see a title, heading, or underlined text, wrap it in double asterisks like **this**.
        - If you see a bulleted or numbered list, keep the bullet/number as-is (e.g. "- " or "1.").
        - If a word is illegible, write [illegible] instead of guessing.
        - Do not translate, summarize, or paraphrase. Transcribe exactly what is written.

        Begin transcription now."""
        response = await client.chat(model=ai_model, messages=[
        {
            "role": "user",
            "content": ocr_prompt,
            "images": [img_buf.getvalue()] # Can be URL or bytes
        }], options={"temperature": settings.ai_temp})

        raw_text = response.message.content

        format_prompt = f"""You are converting raw transcribed notebook text into clean Markdown for Obsidian.

        Rules:
        - Text wrapped in **double asterisks** was a heading, title, or emphasized line in the original. Decide whether it should be a # heading, ## subheading, or **bold** inline text based on context (e.g. first line of the page is likely a top-level heading).
        - Lines starting with "- " or a number followed by "." should become proper Markdown lists.
        - Indented lines should become nested list items.
        - Preserve paragraph breaks as blank lines between paragraphs.
        - Do not add any content that isn't in the source text below.
        - Do not add commentary, explanations, or a preamble. Output ONLY the final Markdown.

        Raw transcribed text:
        ---
        {raw_text}
        ---

        Convert the above into clean Markdown now."""

        formatted_markdown = await client.chat(model=ai_model, messages=[
            {
                "role": "user",
                "content": format_prompt,
            }
        ], options={"temperature": settings.ai_temp})

        final_markdown = re.sub(r'^```(?:markdown)?\n?|\n?```$', '', formatted_markdown.message.content.strip())
        return final_markdown
        # return formatted_markdown.message.content
    except ResponseError as e:
        return f"Error: {e}"

