from absence_calculator.core import (
    AbsentNumber, Void, VOID, Unresolved, ErasureResult, ErasedExcess,
    add, subtract, multiply, divide, erase, erased, negative,
    combine, compare, trace,
    solve, format_result, parse_number, ALL_OPERATIONS
)
from absence_calculator import toggle
from absence_calculator.toggle import tensor


def n(value, absence_level=0):
    return AbsentNumber(value, absence_level)


__version__ = "0.7.7"
