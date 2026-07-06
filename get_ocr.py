from PIL import Image
from io import BytesIO
import pytesseract

def ocr_image_from_url(url=""):
    if url == "":
        return "err: empty url"
    else:
        print(f"FROM get_ocr.py:8 - url: `{url}`")
        return pytesseract.image_to_string(Image.open(url))

async def ocr_image_from_telethon(client, chat_id, msg_id):
    msg = await client.get_messages(chat_id, ids=msg_id)
    if not msg or not msg.media:
        return "err: empty msg"
    buf = BytesIO()
    await msg.download_media(buf)
    buf.seek(0)

    img = Image.open(buf)
    return pytesseract.image_to_string(img)


if __name__ == "__main__":
    img = input('url: ')
    print(ocr_image_from_url(img))