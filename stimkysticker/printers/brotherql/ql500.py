import typing

from ...labels.brotherdk import DK2012, DK2205
from ...labels.label import Label
from .brotherql import BrotherQl


class QL500(BrotherQl):
    name = "QL-500"
    SUPPORTED_LABELS: typing.Tuple[Label] = (DK2012, DK2205)


class QL570(BrotherQl):
    name = "QL-570"
    SUPPORTED_LABELS: typing.Tuple[Label] = (DK2012, DK2205)
