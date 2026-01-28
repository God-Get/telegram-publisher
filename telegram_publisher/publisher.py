from __future__ import annotations

from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message

from .dto import DraftDTO
from .errors import TelegramAPIError


class TelegramPublisher:
    """
    Rules:
    - keyboard is ALWAYS attached to post message (post_message_id)
    - card is a separate message (card_message_id) usually below
    - parse_mode is disabled by default to avoid markdown entity issues in MVP
    """

    def __init__(self, bot: Bot, *, parse_mode: Optional[str] = None):
        self.bot = bot
        self.parse_mode = parse_mode  # keep None by default

    async def upsert_post(self, draft: DraftDTO, keyboard: InlineKeyboardMarkup) -> int:
        """
        Create or edit the post message in a forum topic.
        If draft has image_file_id -> sendPhoto/editMessageCaption
        Else -> sendMessage/editMessageText
        """
        if draft.post_message_id:
            await self._edit_post(draft, keyboard)
            return draft.post_message_id

        msg = await self._send_post(draft, keyboard)
        draft.post_message_id = msg.message_id
        return draft.post_message_id

    async def upsert_card(self, draft: DraftDTO, card_text: str) -> int:
        """
        Create or edit service card message (no critical keyboard by default).
        """
        if draft.card_message_id:
            await self._safe_edit_text(
                chat_id=draft.group_chat_id,
                message_id=draft.card_message_id,
                text=card_text,
            )
            return draft.card_message_id

        msg = await self.bot.send_message(
            chat_id=draft.group_chat_id,
            message_thread_id=draft.topic_id,
            text=card_text,
            parse_mode=self.parse_mode,
            disable_web_page_preview=True,
        )
        draft.card_message_id = msg.message_id
        return draft.card_message_id

    async def move_post_and_card(self, draft: DraftDTO, to_topic_id: int, keyboard: InlineKeyboardMarkup, card_text: str) -> None:
        """
        Telegram doesn't provide real "move message between topics".
        We re-post in new topic and delete old.
        """
        old_post_id = draft.post_message_id
        old_card_id = draft.card_message_id

        # switch topic
        draft.topic_id = to_topic_id
        draft.post_message_id = None
        draft.card_message_id = None

        await self.upsert_post(draft, keyboard)
        await self.upsert_card(draft, card_text)

        # delete old
        if old_post_id:
            await self.safe_delete(draft.group_chat_id, old_post_id)
        if old_card_id:
            await self.safe_delete(draft.group_chat_id, old_card_id)

    async def publish_to_channel(self, draft: DraftDTO) -> int:
        """
        Publish to channel_chat_id.
        If image exists -> sendPhoto with caption
        else -> sendMessage
        """
        if not draft.channel_chat_id:
            raise TelegramAPIError("channel_chat_id is not set")

        try:
            if draft.tg_image_file_id:
                msg = await self.bot.send_photo(
                    chat_id=draft.channel_chat_id,
                    photo=draft.tg_image_file_id,
                    caption=draft.post_text_ru,
                    parse_mode=self.parse_mode,
                )
            else:
                msg = await self.bot.send_message(
                    chat_id=draft.channel_chat_id,
                    text=draft.post_text_ru,
                    parse_mode=self.parse_mode,
                    disable_web_page_preview=True,
                )
        except TelegramBadRequest as e:
            raise TelegramAPIError(str(e)) from e

        draft.published_message_id = msg.message_id
        return msg.message_id

    async def safe_delete(self, chat_id: int, message_id: int) -> None:
        try:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            # ignore
            return

    # -------------------- internals --------------------

    async def _send_post(self, draft: DraftDTO, keyboard: InlineKeyboardMarkup) -> Message:
        try:
            if draft.tg_image_file_id:
                return await self.bot.send_photo(
                    chat_id=draft.group_chat_id,
                    message_thread_id=draft.topic_id,
                    photo=draft.tg_image_file_id,
                    caption=draft.post_text_ru,
                    parse_mode=self.parse_mode,
                    reply_markup=keyboard,
                )
            return await self.bot.send_message(
                chat_id=draft.group_chat_id,
                message_thread_id=draft.topic_id,
                text=draft.post_text_ru,
                parse_mode=self.parse_mode,
                disable_web_page_preview=True,
                reply_markup=keyboard,
            )
        except TelegramBadRequest as e:
            raise TelegramAPIError(str(e)) from e

    async def _edit_post(self, draft: DraftDTO, keyboard: InlineKeyboardMarkup) -> None:
        assert draft.post_message_id is not None

        try:
            if draft.tg_image_file_id:
                # easiest: update caption + keyboard
                await self.bot.edit_message_caption(
                    chat_id=draft.group_chat_id,
                    message_id=draft.post_message_id,
                    caption=draft.post_text_ru,
                    parse_mode=self.parse_mode,
                    reply_markup=keyboard,
                )
            else:
                await self.bot.edit_message_text(
                    chat_id=draft.group_chat_id,
                    message_id=draft.post_message_id,
                    text=draft.post_text_ru,
                    parse_mode=self.parse_mode,
                    disable_web_page_preview=True,
                    reply_markup=keyboard,
                )
        except TelegramBadRequest as e:
            raise TelegramAPIError(str(e)) from e

    async def _safe_edit_text(self, chat_id: int, message_id: int, text: str) -> None:
        try:
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=self.parse_mode,
                disable_web_page_preview=True,
            )
        except TelegramBadRequest:
            # if message was deleted or can't be edited -> try to ignore
            return
