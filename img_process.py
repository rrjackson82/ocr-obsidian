from io import BytesIO

async def convert_img_to_bytes(client, chat_id, msg_id):
    msg = await client.get_messages(chat_id, ids=msg_id)
    if not msg or not msg.media:
        return "err: empty message"

    buf = BytesIO()
    await msg.download_media(buf)
    buf.seek(0)

    return buf
