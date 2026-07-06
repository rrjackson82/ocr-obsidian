from PIL import Image
from io import BytesIO
import pytesseract
from img_process import convert_img_to_bytes

def ocr_image_from_url(url=""):
    if url == "":
        return "err: empty url"
    else:
        print(f"FROM get_ocr.py:8 - url: `{url}`")
        return pytesseract.image_to_string(Image.open(url))

async def ocr_image_from_telethon(client, chat_id, msg_id):
    buf = await convert_img_to_bytes(client, chat_id, msg_id)

    img = Image.open(buf)
    return pytesseract.image_to_string(img)


if __name__ == "__main__":
    img = input('url: ')
    print(ocr_image_from_url(img))