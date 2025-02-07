import io
import os
import uuid
from typing import List, Union

from aiogram import types, Bot
from aiogram.utils.media_group import MediaGroupBuilder


async def downloading(
        message: types.Message,
        album: List[types.Message],
) -> Union[str, None]:
    if not album:
        album = [message]

    paths = []
    for msg in album:
        type_msg = msg.content_type.value
        if type_msg == 'photo':
            media = getattr(msg, type_msg)[-1]
            path = f'./photos/{media.file_id}'
            os.makedirs(path, exist_ok=True)

            file_uuid = str(uuid.uuid4())
            dest_path = os.path.join(path, file_uuid + '.png')
            await msg.bot.download(media.file_id, dest_path)
            paths.append(dest_path)
        elif type_msg == 'document':
            media = getattr(msg, type_msg)
            path = './documents'
            os.makedirs(path, exist_ok=True)

            file_uuid = str(uuid.uuid4())
            dest_path = os.path.join(path, file_uuid + '_' + media.file_name)
            await msg.bot.download(media.file_id, dest_path)
            paths.append(dest_path)
        
        return paths
            

    return paths


async def copy_post(
        data: Union[List[types.Message], types.Message],
        chat_id: int,
        bot: Bot,
        caption_add: str = None,
        replace_caption: bool = False
):
    async def get_media(
            data_: Union[List[types.Message], types.Message],
            caption_add_: str = None,
            replace_caption_: bool = False
    ):
        if isinstance(data_, list):
            caption = getattr(data_[0], 'html_text', '')
            if caption_add_:
                if replace_caption_:
                    caption = caption
                else:
                    caption += caption_add_
            media_group = MediaGroupBuilder(caption=caption)
            for msg in data_:
                type_msg = msg.content_type.value
                try:
                    media = getattr(msg, type_msg)[0].file_id
                except TypeError:
                    media = getattr(msg, type_msg).file_id
                media_group.add(type=type_msg, media=media, parse_mode='HTML')

            return media_group
        else:
            message = data_
            if caption_add_:
                upd = {}
                if message.content_type.value == 'text':
                    upd['text'] = (message.text or '') + caption_add_
                else:
                    upd['caption'] = (message.caption or '') + caption_add_
                message = message.model_copy(update=upd)
            return message

    data = await get_media(data, caption_add, replace_caption_=replace_caption)
    if isinstance(data, types.Message):
        return [await bot(data.send_copy(chat_id))]
    else:
        return await bot.send_media_group(chat_id, data.build())
