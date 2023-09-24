from .brotherdk import DK2012, DK2205
from .generic import GenericCSNA2Roll

ALL_LABELS = (DK2012, DK2205, GenericCSNA2Roll)
LABELS_DICT = {
    DK2012.name.casefold(): DK2012,
    DK2205.name.casefold(): DK2205,
    GenericCSNA2Roll.name.casefold(): GenericCSNA2Roll,
}
