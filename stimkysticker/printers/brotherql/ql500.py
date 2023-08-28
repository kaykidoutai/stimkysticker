from ...labels.brotherdk import DK2012, DK2205
from .brotherql import BrotherQl


class QL500(BrotherQl):
    name = "QL-500"
    SUPPORTED_LABELS = (DK2012, DK2205)
