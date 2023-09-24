import typing
from asyncio.subprocess import PIPE, STDOUT, create_subprocess_shell
from pathlib import Path
from PIL import Image, ImageOps
import serial

from stimkysticker.labels.brotherdk import BrotherDK

from ..labels.label import Label
from .printer import Printer, StimkyPrinterException


class CSNA2T:
    usb_dev: Path = Path("/dev/ttyUSB0")
    name: str
    SUPPORTED_LABELS: typing.Tuple[Label]
    baud_rate: int = 19200

    def __init__(self):
        self._serial = serial.Serial(str(CSNA2T.usb_dev), CSNA2T.baud_rate)
        self._printer_init()

    def _printer_init(self):
        for command in CSNA2T.PRINT_INIT_SEQUENCE:
            self._serial.write(int(command).to_bytes())

    def printer_test(self):
        for command in CSNA2T.PRINT_INIT_SEQUENCE:
            self._serial.write(command)
        for char in "hello world!\n":
            self._serial.write(char.encode())

    def resize_image(self, image: Image):
        # Rotate landscape images to be portrait
        if image.width > image.height:
            image = image.rotate(90, expand=True)

    def print_bitmap(self):
        img = self.image_to_bitmap()
        COMMANDS = [18, 86, 255, 0]
        for command in COMMANDS:
            self._serial.write(int(command).to_bytes())
        cursor = 0
        for y in range(0, 255):
            for x in range(0, 48):
                print(cursor)
                self._serial.write(int(img[cursor]).to_bytes())
                cursor += 1
        self._serial.write("\n".encode())
        self._serial.write("\n".encode())
        self._serial.write("\n".encode())

    async def print(self, image_file: Path) -> Path:
        if not self.usb_dev.exists():
            raise StimkyPrinterException(
                f"USB device {self.usb_dev} for {self.name} does not exist"
            )
        formatted_image = self._label.format_image_for_grayscale_label(image=image_file)

        return formatted_image


async def user_in_dialout() -> bool:
    proc = await create_subprocess_shell("groups", stdout=PIPE, stderr=STDOUT)
    out, err = await proc.communicate()
    return "dialout" in out.decode().split()
