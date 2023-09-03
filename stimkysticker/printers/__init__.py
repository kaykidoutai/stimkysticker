from .brotherql.ql500 import QL500
from .brotherql.qldummy import QLDummy

ALL_PRINTERS = (QL500, QLDummy)
PRINTER_DICT = {QL500.name.casefold(): QL500, QLDummy.name.casefold(): QLDummy}
