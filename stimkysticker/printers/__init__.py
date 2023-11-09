from .brotherql.ql500 import QL500, QL570
from .brotherql.qldummy import QLDummy
from .csn_a2_t import CSNA2T

ALL_PRINTERS = (QL500, QLDummy, CSNA2T)
PRINTER_DICT = {
    QL500.name.casefold(): QL500,
    QL570.name.casefold(): QL570,
    QLDummy.name.casefold(): QLDummy,
    CSNA2T.name.casefold(): CSNA2T,
}
