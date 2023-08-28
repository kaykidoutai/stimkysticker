import typing
from abc import ABC
from pathlib import Path

from ..labels.label import Label
from ..utils.exceptions import StimkyStickerException


class Printer(ABC):
    SUPPORTED_LABELS: typing.Tuple[Label]
    name: str

    def __init__(self, using_label: Label):
        self._label = using_label
        if self._label not in self.SUPPORTED_LABELS:
            raise StimkyPrinterException(
                f"Label {self._label.name} is not supported by printer {self.name}"
            )

    async def print(self, image_file: Path) -> Path:
        ...


class StimkyPrinterException(StimkyStickerException):
    def __init__(self, message: str):
        self.message = message
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
