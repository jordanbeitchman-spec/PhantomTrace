from absence_calculator.core import (
    AbsentNumber, Void, VOID, Unresolved, ErasureResult, ErasedExcess,
    add, subtract, multiply, divide, erase, erased, negative,
    combine, compare, trace,
    present, absent, smallest, largest, ordering,
    solve, format_result, parse_number, ALL_OPERATIONS
)
from absence_calculator import toggle
from absence_calculator.toggle import tensor
from absence_calculator import builder
from absence_calculator.builder import StateSpace, State, StateNumber, StateTransition, StateRule, presence_absence_space


def n(value, absence_level=0):
    return AbsentNumber(value, absence_level)


__version__ = "0.8.0"
