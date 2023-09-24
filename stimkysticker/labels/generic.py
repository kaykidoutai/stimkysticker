import typing

from attr import dataclass

from stimkysticker.labels.label import Label


@dataclass(frozen=True)
class Generic(Label):
    width_mm: int


GenericCSNA2Roll = Generic(
    width_px=384,
    height_px=None,
    height_px_max=1275,
    width_mm=52,
    name="GENERIC-CSNA2-ROLL",
)
