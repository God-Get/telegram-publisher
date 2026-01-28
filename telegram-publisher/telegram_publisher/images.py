from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from aiogram.types import BufferedInputFile, FSInputFile, InputFile


@dataclass(frozen=True)
class ImageFileId:
    file_id: str


@dataclass(frozen=True)
class ImageBytes:
    data: bytes
    filename: str = "image.jpg"


@dataclass(frozen=True)
class ImagePath:
    path: str | Path


ImageInput = Union[ImageFileId, ImageBytes, ImagePath]


def to_photo(image: ImageInput) -> str | InputFile:
    if isinstance(image, ImageFileId):
        return image.file_id
    if isinstance(image, ImageBytes):
        return BufferedInputFile(image.data, filename=image.filename)
    if isinstance(image, ImagePath):
        return FSInputFile(str(image.path))
    raise TypeError(f"Unsupported image type: {type(image)!r}")
