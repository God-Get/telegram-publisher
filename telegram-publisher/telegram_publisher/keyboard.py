from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@dataclass(frozen=True)
class Btn:
    text: str
    callback_data: str | None = None
    url: str | None = None

    def to_aiogram(self) -> InlineKeyboardButton:
        if (self.callback_data is None) == (self.url is None):
            raise ValueError("Btn must have exactly one of: callback_data or url")
        return InlineKeyboardButton(text=self.text, callback_data=self.callback_data, url=self.url)


def kb(rows: Sequence[Sequence[Btn]]) -> InlineKeyboardMarkup:
    inline_rows: List[List[InlineKeyboardButton]] = []
    for r in rows:
        inline_rows.append([b.to_aiogram() for b in r])
    return InlineKeyboardMarkup(inline_keyboard=inline_rows)


def kb_row(*buttons: Btn) -> InlineKeyboardMarkup:
    return kb([list(buttons)])
