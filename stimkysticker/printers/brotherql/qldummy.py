import typing
from pathlib import Path

from PIL import Image

from ...labels.brotherdk import DK2012, DK2205
from ...labels.label import Label
from .brotherql import BrotherQl


class QLDummy(BrotherQl):
    name = "QLDummy"
    SUPPORTED_LABELS: typing.Tuple[Label] = (DK2012, DK2205)

    async def print(self, image_file: Path) -> Path:
        img_path = self._label.format_image_for_grayscale_label(image=image_file)
        pil_img = Image.open(img_path)
        pil_img.show(title="Your Label")
        return img_path
