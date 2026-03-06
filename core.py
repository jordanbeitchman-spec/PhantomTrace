import ast
import operator


class Void:
    def __repr__(self):
        return "void"

    def __eq__(self, other):
        return isinstance(other, Void)

VOID = Void()


class AbsentNumber:
    def __init__(self, value, absence_level=0):
        if value == 0:
            value = 1
            absence_level += 1
        self.value = value
        self.absence_level = absence_level % 2

    @property
    def state(self):
        return "absent" if self.absence_level == 1 else "present"

    @property
    def is_present(self):
        return self.absence_level == 0

    @property
    def is_absent(self):
        return self.absence_level == 1

    def apply_absence(self):
        return AbsentNumber(self.value, self.absence_level + 1)

    def toggle(self):
        return AbsentNumber(self.value, self.absence_level + 1)

    def __call__(self, level):
        if level == 0:
            return AbsentNumber(self.value, self.absence_level + 1)
        elif level == 1:
            return AbsentNumber(self.value, self.absence_level)
        else:
            return multiply(AbsentNumber(self.value, self.absence_level), AbsentNumber(level))

    def _format_value(self):
        if isinstance(self.value, float) and self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)

    def __repr__(self):
        if self.value == 1 and self.absence_level == 1:
            return "0"
        v = self._format_value()
        if self.absence_level == 0:
            return v
        else:
            return f"{v}(0)"

    def __eq__(self, other):
        if isinstance(other, AbsentNumber):
            return self.value == other.value and self.absence_level == other.absence_level
        return False


class ErasedExcess:
    def __init__(self, value, absence_level=0, erasure_level=1):
        self.value = value
        self.absence_level = absence_level % 2
        self.erasure_level = erasure_level

    def apply_absence(self):
        return ErasedExcess(self.value, self.absence_level + 1, self.erasure_level)

    def _format_value(self):
        if isinstance(self.value, float) and self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)

    def __repr__(self):
        v = self._format_value()
        if self.absence_level == 1:
            v = f"{v}(0)"
        prefix = "erased " * self.erasure_level
        return f"{prefix}{v}"

    def __eq__(self, other):
        if isinstance(other, ErasedExcess):
            return (self.value == other.value and
                    self.absence_level == other.absence_level and
                    self.erasure_level == other.erasure_level)
        return False


class ErasureResult:
    def __init__(self, remainder, erased):
        self.remainder = remainder
        self.erased = erased

    def __repr__(self):
        parts = []
        if self.remainder is not None:
            parts.append(str(self.remainder))
        if self.erased is not None:
            parts.append(str(self.erased))
        return " + ".join(parts) if parts else "void"

    def __eq__(self, other):
        if isinstance(other, ErasureResult):
            return self.remainder == other.remainder and self.erased == other.erased
        return False


class Unresolved:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"

    def __eq__(self, other):
        if isinstance(other, Unresolved):
            return self.left == other.left and self.op == other.op and self.right == other.right
        return False


def _collect_terms(result):
    buckets = {}
    unresolvable = []

    def _collect(r):
        if r is None or isinstance(r, Void):
            return
        if isinstance(r, AbsentNumber):
            key = (r.absence_level, 0)
            buckets[key] = buckets.get(key, 0) + r.value
        elif isinstance(r, ErasedExcess):
            key = (r.absence_level, r.erasure_level)
            buckets[key] = buckets.get(key, 0) + r.value
        elif isinstance(r, ErasureResult):
            _collect(r.remainder)
            _collect(r.erased)
        elif isinstance(r, Unresolved) and r.op == "+":
            _collect(r.left)
            _collect(r.right)
        else:
            unresolvable.append(r)

    _collect(result)

    present = buckets.pop((0, 0), 0)
    absent = buckets.pop((1, 0), 0)
    excesses = buckets
    return present, absent, excesses, unresolvable


def _build_result(present, absent, excesses, unresolvable=None):
    if unresolvable is None:
        unresolvable = []

    levels = {}
    levels[(0, 0)] = present
    levels[(1, 0)] = absent
    for key, val in excesses.items():
        levels[key] = levels.get(key, 0) + val

    max_elevel = max((k[1] for k in levels if levels[k] > 0), default=0)
    for elevel in range(1, max_elevel + 1):
        for abs_level in (0, 1):
            debt_key = (abs_level, elevel)
            target_key = (abs_level, elevel - 1)
            debt = levels.get(debt_key, 0)
            target = levels.get(target_key, 0)
            if debt > 0 and target > 0:
                flipped_key = ((abs_level + 1) % 2, elevel - 1)
                if target >= debt:
                    levels[target_key] = target - debt
                    levels[flipped_key] = levels.get(flipped_key, 0) + debt
                    levels[debt_key] = 0
                else:
                    levels[flipped_key] = levels.get(flipped_key, 0) + target
                    levels[debt_key] = debt - target
                    levels[target_key] = 0

    parts = []
    for (abs_level, elevel) in sorted(levels.keys()):
        val = levels[(abs_level, elevel)]
        if val > 0:
            if elevel == 0:
                parts.append(AbsentNumber(val, abs_level))
            else:
                parts.append(ErasedExcess(val, abs_level, elevel))
    parts.extend(unresolvable)

    if not parts:
        return VOID

    result = parts[0]
    for p in parts[1:]:
        if isinstance(result, AbsentNumber) and isinstance(p, AbsentNumber):
            if result.absence_level == p.absence_level:
                result = AbsentNumber(result.value + p.value, result.absence_level)
            else:
                result = Unresolved(result, "+", p)
        elif isinstance(p, ErasedExcess):
            result = ErasureResult(result, p)
        else:
            result = Unresolved(result, "+", p)

    return result


def _is_tensor(x):
    return isinstance(x, list)


def _add_scalar(x, y):
    if isinstance(x, AbsentNumber) and isinstance(y, AbsentNumber):
        if x.absence_level == y.absence_level:
            return AbsentNumber(x.value + y.value, x.absence_level)
        else:
            return Unresolved(x, "+", y)

    px, ax, ex, ux = _collect_terms(x)
    py, ay, ey, uy = _collect_terms(y)
    merged = dict(ex)
    for k, v in ey.items():
        merged[k] = merged.get(k, 0) + v
    return _build_result(px + py, ax + ay, merged, ux + uy)


def add(x, y):
    if _is_tensor(x) and _is_tensor(y):
        if len(x) != len(y):
            raise ValueError(f"Cannot add tensors of different sizes: {len(x)} vs {len(y)}")
        return [add(xi, yi) for xi, yi in zip(x, y)]
    if _is_tensor(x) or _is_tensor(y):
        raise ValueError("Cannot add a tensor and a scalar")
    return _add_scalar(x, y)


def _subtract_scalar(x, y):
    if isinstance(x, AbsentNumber) and isinstance(y, AbsentNumber):
        if x.absence_level != y.absence_level:
            return Unresolved(x, "-", y)
        if x.value == y.value:
            return VOID
        if x.value > y.value:
            return AbsentNumber(x.value - y.value, x.absence_level)
        else:
            return Unresolved(x, "-", y)

    return Unresolved(x, "-", y)


def subtract(x, y):
    if _is_tensor(x) and _is_tensor(y):
        if len(x) != len(y):
            raise ValueError(f"Cannot subtract tensors of different sizes: {len(x)} vs {len(y)}")
        return [subtract(xi, yi) for xi, yi in zip(x, y)]
    if _is_tensor(x) or _is_tensor(y):
        raise ValueError("Cannot subtract a tensor and a scalar")
    return _subtract_scalar(x, y)


def _multiply_scalar(x, y):
    if isinstance(x, AbsentNumber) and isinstance(y, AbsentNumber):
        result_value = x.value * y.value
        result_level = (x.absence_level + y.absence_level) % 2
        return AbsentNumber(result_value, result_level)

    return Unresolved(x, "*", y)


def multiply(x, y):
    if _is_tensor(x) and _is_tensor(y):
        if len(x) != len(y):
            raise ValueError(f"Cannot multiply tensors of different sizes: {len(x)} vs {len(y)}")
        return [multiply(xi, yi) for xi, yi in zip(x, y)]
    if _is_tensor(x) or _is_tensor(y):
        raise ValueError("Cannot multiply a tensor and a scalar")
    return _multiply_scalar(x, y)


def _divide_scalar(x, y):
    if isinstance(x, AbsentNumber) and isinstance(y, AbsentNumber):
        if y.value == 0:
            return VOID
        result_level = (x.absence_level + y.absence_level) % 2
        if x.value % y.value == 0:
            return AbsentNumber(x.value // y.value, result_level)
        result_value = round(x.value / y.value, 10)
        if result_value == int(result_value):
            return AbsentNumber(int(result_value), result_level)
        return AbsentNumber(result_value, result_level)

    return Unresolved(x, "/", y)


def divide(x, y):
    if _is_tensor(x) and _is_tensor(y):
        if len(x) != len(y):
            raise ValueError(f"Cannot divide tensors of different sizes: {len(x)} vs {len(y)}")
        return [divide(xi, yi) for xi, yi in zip(x, y)]
    if _is_tensor(x) or _is_tensor(y):
        raise ValueError("Cannot divide a tensor and a scalar")
    return _divide_scalar(x, y)


def _erase_scalar(x, y):
    return _add_scalar(x, erased(y))


def erase(x, y):
    if _is_tensor(x) and _is_tensor(y):
        if len(x) != len(y):
            raise ValueError(f"Cannot erase tensors of different sizes: {len(x)} vs {len(y)}")
        return [erase(xi, yi) for xi, yi in zip(x, y)]
    if _is_tensor(x) or _is_tensor(y):
        raise ValueError("Cannot erase a tensor and a scalar")
    return _erase_scalar(x, y)


def erased(x):
    if _is_tensor(x):
        return [erased(xi) for xi in x]
    if isinstance(x, AbsentNumber):
        return ErasedExcess(x.value, x.absence_level, 1)
    if isinstance(x, ErasedExcess):
        return ErasedExcess(x.value, x.absence_level, x.erasure_level + 1)
    return ErasedExcess(x, 0, 1)


def negative(x):
    if _is_tensor(x):
        return [negative(xi) for xi in x]
    if isinstance(x, AbsentNumber):
        return AbsentNumber(-x.value, x.absence_level)
    return AbsentNumber(-x, 0)


def _find_top_level_op(expr):
    depth = 0
    rightmost_low = None
    rightmost_high = None

    i = 0
    while i < len(expr):
        c = expr[i]
        if c == '(':
            depth += 1
            i += 1
        elif c == ')':
            depth -= 1
            i += 1
        elif depth == 0:
            remaining = expr[i:]
            if (remaining.startswith('erased')
                    and i > 0
                    and (len(remaining) <= 6 or not remaining[6].isalnum())):
                prev = expr[:i].rstrip()
                if prev and (prev[-1].isdigit() or prev[-1] == ')'):
                    rightmost_low = (i, 'erased')
                i += 6
            elif c in '+-' and i > 0:
                j = i - 1
                while j >= 0 and expr[j] == ' ':
                    j -= 1
                if j >= 0 and (expr[j].isdigit() or expr[j] == ')'):
                    rightmost_low = (i, c)
                i += 1
            elif c in '*/':
                rightmost_high = (i, c)
                i += 1
            else:
                i += 1
        else:
            i += 1

    if rightmost_low is not None:
        return rightmost_low
    if rightmost_high is not None:
        return rightmost_high
    return None, None


def solve(expr_string):
    expr_string = expr_string.strip()

    if not expr_string:
        return VOID

    pos, op = _find_top_level_op(expr_string)

    if pos is not None:
        if op == 'erased':
            left_str = expr_string[:pos].strip()
            right_str = expr_string[pos + 6:].strip()
        else:
            left_str = expr_string[:pos].strip()
            right_str = expr_string[pos + 1:].strip()

        left = solve(left_str)
        right = solve(right_str)

        if op == '+':
            return add(left, right)
        elif op == '-':
            return subtract(left, right)
        elif op == '*':
            return multiply(left, right)
        elif op == '/':
            return divide(left, right)
        elif op == 'erased':
            return erase(left, right)

    if expr_string.startswith('('):
        depth = 0
        match_pos = -1
        for i, c in enumerate(expr_string):
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    match_pos = i
                    break

        if match_pos >= 0:
            inner = expr_string[1:match_pos]
            rest = expr_string[match_pos + 1:]

            if inner == '0' and (rest == '' or all(rest[j:j+3] == '(0)' for j in range(0, len(rest), 3))):
                return parse_number(expr_string)

            result = solve(inner)

            while rest.startswith('(0)'):
                if isinstance(result, AbsentNumber):
                    result = result.apply_absence()
                rest = rest[3:]

            return result

    if expr_string.startswith('erased '):
        value_str = expr_string[7:].strip()
        num = parse_number(value_str)
        return ErasedExcess(num.value, num.absence_level)

    return parse_number(expr_string)


def parse_number(s):
    s = s.strip()
    absence_level = 0
    while s.endswith("(0)"):
        absence_level += 1
        s = s[:-3]
    if not s:
        return AbsentNumber(1, absence_level)
    value = float(s)
    if value == int(value):
        value = int(value)
    return AbsentNumber(value, absence_level)


def combine(x, y):
    if _is_tensor(x) and _is_tensor(y):
        if len(x) != len(y):
            raise ValueError(f"Cannot combine tensors of different sizes: {len(x)} vs {len(y)}")
        return [combine(xi, yi) for xi, yi in zip(x, y)]
    if _is_tensor(x) or _is_tensor(y):
        raise ValueError("Cannot combine a tensor and a scalar")
    x_void = isinstance(x, Void)
    y_void = isinstance(y, Void)
    if x_void and y_void:
        return VOID
    if x_void:
        y_num = y if isinstance(y, AbsentNumber) else AbsentNumber(y, 0)
        return AbsentNumber(1, y_num.absence_level)
    if y_void:
        x_num = x if isinstance(x, AbsentNumber) else AbsentNumber(x, 0)
        return AbsentNumber(1, x_num.absence_level)
    x_num = x if isinstance(x, AbsentNumber) else AbsentNumber(x, 0)
    y_num = y if isinstance(y, AbsentNumber) else AbsentNumber(y, 0)
    x_state = AbsentNumber(1, x_num.absence_level)
    y_state = AbsentNumber(1, y_num.absence_level)
    return add(x_state, y_state)


def compare(x, y):
    if _is_tensor(x) and _is_tensor(y):
        if len(x) != len(y):
            raise ValueError(f"Cannot compare tensors of different sizes: {len(x)} vs {len(y)}")
        return [compare(xi, yi) for xi, yi in zip(x, y)]
    if _is_tensor(x) or _is_tensor(y):
        raise ValueError("Cannot compare a tensor and a scalar")
    px1, ax1, _, _ = _collect_terms(x)
    px2, ax2, _, _ = _collect_terms(y)
    diff = px2 - px1
    if diff > 0:
        return AbsentNumber(diff, 0)
    elif diff < 0:
        return AbsentNumber(abs(diff), 1)
    else:
        return VOID


def _absent_order(num):
    if num.is_absent:
        return -num.value
    else:
        return num.value


def _order_to_absent_number(order_val):
    if order_val < 0:
        return AbsentNumber(abs(order_val), 1)
    elif order_val == 0:
        return AbsentNumber(0, 0)
    else:
        return AbsentNumber(order_val, 0)


def trace(fn, start=None, end=None):
    if isinstance(start, Void) or isinstance(end, Void):
        raise ValueError("Cannot trace over void — void is no calculation")
    if start is not None and end is not None:
        if not isinstance(start, AbsentNumber):
            start = AbsentNumber(start, 0)
        if not isinstance(end, AbsentNumber):
            end = AbsentNumber(end, 0)
        start_ord = _absent_order(start)
        end_ord = _absent_order(end)
        step = 1 if end_ord >= start_ord else -1
        results = []
        current = start_ord
        while (step > 0 and current <= end_ord) or (step < 0 and current >= end_ord):
            if current == 0:
                current += step
                continue
            results.append(fn(_order_to_absent_number(current)))
            current += step
        return results
    return _UnboundTrace(fn, start, end)


class _UnboundTrace:
    def __init__(self, fn, start=None, end=None):
        self.fn = fn
        self.start = start
        self.end = end

    def bind(self, *args, start=None, end=None):
        if len(args) == 2:
            start, end = args
        elif len(args) == 1:
            if self.start is not None and start is None and end is None:
                end = args[0]
            elif start is None:
                start = args[0]
        s = start if start is not None else self.start
        e = end if end is not None else self.end
        if s is not None and e is not None:
            return trace(self.fn, s, e)
        return _UnboundTrace(self.fn, s, e)

    def __call__(self, x):
        return self.fn(x)

    def __repr__(self):
        parts = []
        if self.start is not None:
            parts.append(f"start={self.start}")
        if self.end is not None:
            parts.append(f"end={self.end}")
        bound_info = f"({', '.join(parts)})" if parts else "(unbound)"
        return f"trace{bound_info}"


def format_result(result):
    if _is_tensor(result):
        return '[' + ', '.join(format_result(x) for x in result) + ']'
    return str(result)


ALL_OPERATIONS = {
    "addition": {
        "symbol": "+",
        "rule": "Same state: magnitudes combine (domain expansion). Mixed state: unresolved",
        "examples": ["5 + 3 = 8", "7(0) + 3(0) = 10(0)", "7 + 5(0) = 7 + 5(0) [unresolved]"]
    },
    "subtraction": {
        "symbol": "-",
        "rule": "Same state: magnitudes reduce (domain contraction). Equal values: void. Mixed: unresolved",
        "examples": ["7 - 3 = 4", "5(0) - 3(0) = 2(0)", "7 - 7 = void", "7(0) - 5 = 7(0) - 5 [unresolved]"]
    },
    "multiplication": {
        "symbol": "*",
        "rule": "Magnitudes multiply. States combine: present*present=present, absent*present=absent, absent*absent=present",
        "examples": ["10 * 9 = 90", "5(0) * 5 = 25(0)", "25(0) * 4(0) = 100"]
    },
    "division": {
        "symbol": "/",
        "rule": "Magnitudes divide (decimals allowed). States combine same as multiplication",
        "examples": ["90 / 9 = 10", "25(0) / 5 = 5(0)", "6(0) / 8(0) = 0.75", "100(0) / 4(0) = 25"]
    },
    "erasure": {
        "symbol": "erased",
        "rule": "Same state required. Flips state of erased portion, remainder keeps state. Over-erasure creates erased excess",
        "examples": [
            "5 erased 3 = 2 + 3(0)",
            "7 erased 7 = 7(0)",
            "7 erased 10 = 7(0) + erased 3",
            "(erased 3) erased (erased 3) = erased 3(0)"
        ]
    },
    "absence": {
        "symbol": "(0)",
        "rule": "Flips state. x(0) = absent x. x(0)(0) = x (double absence = presence)",
        "examples": ["5(0) = absent 5", "5(0)(0) = 5"]
    }
}
