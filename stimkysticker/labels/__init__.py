from .brotherdk import DK2012, DK2205

ALL_LABELS = (
    DK2012,
    DK2205,
)
LABELS_DICT = {DK2012.name.casefold(): DK2012, DK2205.name.casefold(): DK2205}
