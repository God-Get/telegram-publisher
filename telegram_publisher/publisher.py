from __future__ import annotations

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto

from .images import ImageInput, to_photo


class TelegramPublisher:
    """
    Minimal layer:
    - send_post: sendPhoto (caption=text) into chat_id + message_thread_id (topic)
    - edit_post: editMessageMedia (photo+caption) + reply_markup
    parse_mode defaults to None (safest default).
    """

    def __init__(self, bot: Bot, *, parse_mode: str | None = None):
        self.bot = bot
        self.parse_mode = parse_mode  # None or "HTML" (only if you guarantee escaping)

    async def send_post(
        self,
        *,
        chat_id: int | str,
        thread_id: int | None,
        text: str,
        image: ImageInput,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> int:
        msg = await self.bot.send_photo(
            chat_id=chat_id,
            message_thread_id=thread_id,
            photo=to_photo(image),
            caption=text,
            parse_mode=self.parse_mode,
            reply_markup=reply_markup,
        )
        return msg.message_id

    async def edit_post(
        self,
        *,
        chat_id: int | str,
        post_message_id: int,
        text: str,
        image: ImageInput,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        media = InputMediaPhoto(
            media=to_photo(image),
            caption=text,
            parse_mode=self.parse_mode,
        )
        await self.bot.edit_message_media(
            chat_id=chat_id,
            message_id=post_message_id,
            media=media,
            reply_markup=reply_markup,
        )
