from .labels import LABELS_DICT
from .labels.label import Label
from .printers import PRINTER_DICT
from .printers.printer import Printer


def structure_label(label: Label) -> str:
    return label.name.casefold()


def unstructure_label(raw: str) -> Label:
    if LABELS_DICT.get(raw) is None:
        raise ValueError(
            f"{raw} is an invalid label type. Valid labels are {', '.join(LABELS_DICT.keys())}"
        )
    return LABELS_DICT[raw]


def structure_printer(printer: Printer) -> str:
    return printer.name.casefold()


def unstructure_printer(printer: str, label: str) -> Printer:
    label = unstructure_label(label)
    if PRINTER_DICT.get(printer) is None:
        raise ValueError(
            f"{printer} is not a valid printer. Valid printers are {', '.join(PRINTER_DICT.keys())}"
        )
    return PRINTER_DICT[printer](label)
