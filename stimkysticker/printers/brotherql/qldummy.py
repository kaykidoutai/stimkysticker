import typing
from asyncio.subprocess import PIPE, STDOUT, create_subprocess_shell
from pathlib import Path

from PIL import Image

from stimkysticker.labels.brotherdk import BrotherDK

from ...labels.brotherdk import DK2012, DK2205
from ..printer import Printer, StimkyPrinterException
from .brotherql import BrotherQl


class QLDummy(BrotherQl):
    name = "QL-500"
    SUPPORTED_LABELS = (DK2012, DK2205)

    async def print(self, image_file: Path) -> Path:
        img_path = self._label.format_image_for_label(image=image_file)
        pil_img = Image.open(img_path)
        pil_img.show(title="Your Label")
        return img_path
