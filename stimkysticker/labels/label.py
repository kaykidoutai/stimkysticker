import typing
from abc import ABC
from pathlib import Path

from attr import dataclass
from loguru import logger
from PIL import Image, ImageOps

from ..utils.exceptions import StimkyStickerException


@dataclass(frozen=True)
class Label(ABC):
    name: str
    height_px: typing.Optional[int]  # Handle continuous labels
    height_px_max: int  # Max height to prevent abuse
    width_px: int

    def format_image_for_grayscale_label(self, image: Path) -> Path:
        return self.format_img_grayscale(
            filepath=image,
            width=self.width_px,
            height=self.height_px,
            portrait=self.portrait,
        )

    def format_image_for_bw_label(self, image: Path) -> Path:
        return self.format_img_bw(
            filepath=image,
            width=self.width_px,
            height=self.height_px,
            portrait=self.portrait,
        )

    @property
    def portrait(self) -> bool:
        if self.height_px is None:
            return True
        return self.height_px > self.width_px

    def format_img_grayscale(
        self,
        filepath: Path,
        width: int,
        height: typing.Optional[int],
        portrait: bool,
        background_color: str = "white",
        gamma_correction: float = 1.8,
        file_stem: str = "_formatted",
    ) -> Path:
        if not filepath.exists():
            raise FileNotFoundError(f"Image {filepath} does not exist")
        img = Image.open(filepath)
        img = Label.color_correct_grayscale(
            pil_img=img,
            gamma_correction=gamma_correction,
            background_color=background_color,
        )
        img = self.resize_to_label(
            pil_img=img, width=width, height=height, portrait_label=portrait
        )
        formatted_path = Path(f"{filepath.parent / filepath.stem}{file_stem}.png")
        img.save(f"{formatted_path}", "PNG")
        return formatted_path

    def format_img_bw(
        self,
        filepath: Path,
        width: int,
        height: typing.Optional[int],
        portrait: bool,
        background_color: str = "white",
        file_stem: str = "_formatted",
    ):
        if not filepath.exists():
            raise FileNotFoundError(f"Image {filepath} does not exist")
        img = Image.open(filepath)
        img = Label.color_correct_bw(pil_img=img, background_color=background_color)
        img = self.resize_to_label(
            pil_img=img, width=width, height=height, portrait_label=portrait
        )
        formatted_path = Path(f"{filepath.parent / filepath.stem}{file_stem}.png")
        img.save(f"{formatted_path}", "PNG")
        return formatted_path

    @staticmethod
    def color_correct_grayscale(
        pil_img: Image, gamma_correction: float, background_color: str = "white"
    ):
        if pil_img.mode == "RGBA":
            bg_img = Image.new(pil_img.mode, pil_img.size, background_color)
            pil_img = Image.alpha_composite(bg_img, pil_img)

        # Convert to grayscale and apply a gamma of 1.8
        pil_img = pil_img.convert("L")

        if gamma_correction != 1:
            pil_img = Image.eval(
                pil_img, lambda x: int(255 * pow((x / 255), (1 / gamma_correction)))
            )
        return pil_img

    @staticmethod
    def color_correct_bw(pil_img: Image, background_color: str = "white"):
        if pil_img.mode == "RGBA":
            bg_img = Image.new(pil_img.mode, pil_img.size, background_color)
            pil_img = Image.alpha_composite(bg_img, pil_img)
        pil_img = pil_img.convert("1")
        return pil_img

    def resize_to_label(
        self,
        pil_img: Image,
        width: int,
        height: typing.Optional[int],
        portrait_label: bool,
        color: str = "white",
    ):
        img_width, img_height = pil_img.size
        portrait_photo = img_height > img_width
        if portrait_label != portrait_photo:
            # Flip the image if the label and photo are mismatched aspect ratios
            pil_img = pil_img.rotate(90, expand=1)
            img_width, img_height = pil_img.size
        aspect_ratio = img_height / img_width
        # find the new height if there's no limit
        if height is None:
            height = int(width * aspect_ratio)
            # Check to make sure it's not too tall and would eat too much label
            if height > self.height_px_max:
                raise StimkyLabelException(
                    f"Attempting to resize this image to {width}x{height}. The height is too "
                    f"long and will eat too much label! Please try an image with a squarer "
                    f"aspect ratio"
                )

        # Resize to fit the label`
        return ImageOps.pad(pil_img, (width, height), centering=(0.5, 0.5), color=color)


class StimkyLabelException(StimkyStickerException):
    def __init__(self, message: str):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
