from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DraftDTO:
    draft_id: int

    group_chat_id: int
    topic_id: int

    # Post content
    post_text_ru: str
    source_url: str = ""

    # Image: prefer tg file_id (fast + stable). source_image_url optional for future.
    tg_image_file_id: Optional[str] = None
    source_image_url: Optional[str] = None

    # Telegram ids managed by caller (persist in DB)
    post_message_id: Optional[int] = None
    card_message_id: Optional[int] = None

    # Publishing
    channel_chat_id: Optional[int] = None
    published_message_id: Optional[int] = None
