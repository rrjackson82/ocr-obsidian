from PIL import Image
import pytesseract

def ocr_image(url=""):
    if url == "":
        return "err: empty url"
    else:
        with open(url, 'r') as f:
            if not f:
                return "err: invalid url"
        print(f"FROM get_ocr.py:8 - url: `{url}`")
        return pytesseract.image_to_string(Image.open(url))


img = input('url: ')

print(ocr_image(img))