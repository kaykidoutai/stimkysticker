import typing
from abc import ABC, abstractmethod
from pathlib import Path
from asyncio import Lock

from ..labels.label import Label
from ..utils.exceptions import StimkyStickerException


class Printer(ABC):
    SUPPORTED_LABELS: typing.Tuple[Label]
    name: str
    _printer_lock: Lock = Lock()

    def __init__(self, using_label: Label):
        self._label = using_label
        if self._label not in self.SUPPORTED_LABELS:
            raise StimkyPrinterException(
                f"Label {self._label.name} is not supported by printer {self.name}"
            )

    async def print(self, image_file: Path) -> Path:
        async with self._printer_lock:
            return await self._print(image_file=image_file)

    @abstractmethod
    async def _print(self, image_file: Path) -> Path:
        ...



class StimkyPrinterException(StimkyStickerException):
    def __init__(self, message: str):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
