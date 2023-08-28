import typing

from attr import dataclass

from stimkysticker.labels.label import Label


@dataclass(frozen=True)
class BrotherDK(Label):
    width_mm: int
    height_mm: typing.Optional[int]  # Handle continuous labels

    @property
    def size_str(self) -> str:
        if self.width_mm:
            return f"{self.width_mm}x{self.height_mm}"
        else:
            return f"{self.width_mm}"


DK2012 = BrotherDK(
    width_px=696,
    height_px=1109,
    height_px_max=1109,
    width_mm=62,
    height_mm=100,
    name="DK2012",
)


DK2205 = BrotherDK(
    width_px=696,
    width_mm=62,
    height_px=None,
    height_px_max=2500,
    height_mm=None,
    name="DK2205",
)
