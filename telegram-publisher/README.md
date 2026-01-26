# telegram-publisher

Aiogram 3.x helper to manage:
- Post message (with keyboard) inside forum topics
- Card message (service status) under the post
- "Move" by reposting into another topic
- Publish to channel

## Install (dev)
poetry add git+https://github.com/God-Get/telegram-publisher.git

## Usage
```py
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_publisher import TelegramPublisher, DraftDTO

bot = Bot(token="TOKEN")
pub = TelegramPublisher(bot, parse_mode=None)

kb = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text="Publish", callback_data="draft:1:publish")]
])

d = DraftDTO(
  draft_id=1,
  group_chat_id=-100123,
  topic_id=2,
  post_text_ru="Привет!",
  tg_image_file_id=None,
)

post_id = await pub.upsert_post(d, kb)
card_id = await pub.upsert_card(d, "Draft #1 | READY")
