import ast
import operator as op_module
from absence_calculator.core import AbsentNumber, add


_SAFE_OPS = {
    ast.Add: op_module.add,
    ast.Sub: op_module.sub,
    ast.Mult: op_module.mul,
    ast.Div: op_module.truediv,
    ast.FloorDiv: op_module.floordiv,
    ast.Mod: op_module.mod,
    ast.Pow: op_module.pow,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        func = _SAFE_OPS.get(type(node.op))
        if func is None:
            raise ValueError(f"Unsupported operator in pattern")
        return func(left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.UAdd):
            return operand
        raise ValueError("Unsupported unary operator in pattern")
    else:
        raise ValueError(f"Unsupported expression in pattern: {ast.dump(node)}")


def _safe_eval_pattern(expr_str, x_val):
    expr = expr_str.replace('^', '**')
    expr = expr.replace('x', str(x_val))
    tree = ast.parse(expr, mode='eval')
    return _eval_node(tree.body)


def _to_absent_number(item):
    if isinstance(item, AbsentNumber):
        return AbsentNumber(item.value, item.absence_level)
    elif isinstance(item, (int, float)):
        return AbsentNumber(item, 0)
    else:
        raise TypeError(f"Cannot convert {type(item).__name__} to AbsentNumber")


def _compute_target_indices(pattern, range_tuple, vector_len):
    start, end = range_tuple
    targets = set()
    search_limit = max(vector_len * 4, 200)
    for i in range(-search_limit, search_limit + 1):
        try:
            if callable(pattern):
                target_index = int(pattern(i))
            else:
                target_index = int(_safe_eval_pattern(pattern, i))
        except (ValueError, ZeroDivisionError, OverflowError):
            continue
        if start <= target_index <= end and 0 <= target_index < vector_len:
            targets.add(target_index)
    return targets


def rank(data):
    if isinstance(data, AbsentNumber) or not isinstance(data, list):
        return 0
    if len(data) == 0:
        return 1
    return 1 + rank(data[0])


def shape(data):
    if rank(data) == 0:
        return ()
    dims = []
    current = data
    while isinstance(current, list):
        dims.append(len(current))
        if len(current) > 0:
            current = current[0]
        else:
            break
    return tuple(dims)


def tensor(dimensions, fill='absent', seed=None):
    import hashlib
    if isinstance(dimensions, int):
        dimensions = (dimensions,)

    total = 1
    for d in dimensions:
        total *= d

    present_set = None
    if seed is not None:
        ranked = []
        for i in range(total):
            h = hashlib.sha256(f"phantomtrace_pos_{i}".encode()).hexdigest()
            ranked.append((int(h, 16), i))
        ranked.sort()
        ordering = [pos for _, pos in ranked]
        num_present = seed % (total + 1)
        present_set = set(ordering[:num_present])

    counter = [0]

    def _build(dims):
        if len(dims) == 0:
            if fill == 'absent':
                return AbsentNumber(1, 1)
            else:
                return AbsentNumber(1, 0)
        size = dims[0]
        if len(dims) == 1:
            result = []
            for i in range(size):
                val = i + 1
                if present_set is not None:
                    abs_level = 0 if counter[0] in present_set else 1
                else:
                    abs_level = 1 if fill == 'absent' else 0
                result.append(AbsentNumber(val, abs_level))
                counter[0] += 1
            return result
        return [_build(dims[1:]) for _ in range(size)]

    return _build(dimensions)


def _map_deep(fn, data):
    if isinstance(data, AbsentNumber):
        return fn(data)
    if isinstance(data, list):
        return [_map_deep(fn, item) for item in data]
    return fn(_to_absent_number(data))


def _zip_deep(fn, a, b):
    if isinstance(a, AbsentNumber) or not isinstance(a, list):
        aa = a if isinstance(a, AbsentNumber) else _to_absent_number(a)
        bb = b if isinstance(b, AbsentNumber) else _to_absent_number(b)
        return fn(aa, bb)
    return [_zip_deep(fn, ai, bi) for ai, bi in zip(a, b)]


def _where_vector(pattern, range_tuple, vector):
    result = [_to_absent_number(v) for v in vector]
    targets = _compute_target_indices(pattern, range_tuple, len(result))
    for idx in targets:
        result[idx] = result[idx].toggle()
    return result


def _exclude_vector(pattern, range_tuple, vector):
    result = [_to_absent_number(v) for v in vector]
    targets = _compute_target_indices(pattern, range_tuple, len(result))
    for idx in range(len(result)):
        if idx not in targets:
            result[idx] = result[idx].toggle()
    return result


def _all_vector(vector):
    return [_to_absent_number(v).toggle() for v in vector]


def _apply_along_axis(fn, data, axis, current_depth=0):
    r = rank(data)
    if r == 0:
        return fn(data)
    if axis < 0:
        axis = r + axis
    if current_depth == axis:
        return fn(data)
    return [_apply_along_axis(fn, sub, axis, current_depth + 1) for sub in data]


def where(pattern, range_tuple, data, axis=-1):
    r = rank(data)
    if r <= 1:
        return _where_vector(pattern, range_tuple, data)
    return _apply_along_axis(
        lambda vec: _where_vector(pattern, range_tuple, vec),
        data, axis
    )


def exclude(pattern, range_tuple, data, axis=-1):
    r = rank(data)
    if r <= 1:
        return _exclude_vector(pattern, range_tuple, data)
    return _apply_along_axis(
        lambda vec: _exclude_vector(pattern, range_tuple, vec),
        data, axis
    )


def all(data):
    return _map_deep(lambda x: x.toggle(), data)


def select(data, axis, index):
    r = rank(data)
    if r == 0:
        return data
    if axis < 0:
        axis = r + axis
    if axis == 0:
        return data[index]
    return [select(sub, axis - 1, index) for sub in data]


def assign(data, axis, index, value):
    r = rank(data)
    if r == 0:
        return value
    if axis < 0:
        axis = r + axis
    if axis == 0:
        result = [row for row in data]
        result[index] = value
        return result
    return [assign(sub, axis - 1, index, value) for sub in data]


def across(data, axis, fn):
    r = rank(data)
    if r == 0:
        return data
    if axis < 0:
        axis = r + axis
    if axis == 0:
        result = data[0]
        for i in range(1, len(data)):
            result = _zip_deep(fn, result, data[i])
        return result
    return [across(sub, axis - 1, fn) for sub in data]


def count_present(data, axis=None):
    if axis is None:
        total = 0
        def _count(d):
            nonlocal total
            if isinstance(d, AbsentNumber):
                if d.is_present:
                    total += 1
            elif isinstance(d, list):
                for item in d:
                    _count(item)
        _count(data)
        return total
    return _apply_along_axis(
        lambda vec: sum(1 for v in vec if isinstance(v, AbsentNumber) and v.is_present),
        data, axis
    )


def present_indices(data):
    if rank(data) != 1:
        raise ValueError("present_indices only works on vectors (rank 1)")
    return [i for i, v in enumerate(data) if isinstance(v, AbsentNumber) and v.is_present]


def intersect(a, b):
    def _intersect_fn(x, y):
        if x.is_present and y.is_present:
            return AbsentNumber(x.value, 0)
        return AbsentNumber(x.value, 1)
    return _zip_deep(_intersect_fn, a, b)


def union(a, b):
    def _union_fn(x, y):
        if x.is_present or y.is_present:
            return AbsentNumber(x.value, 0)
        return AbsentNumber(x.value, 1)
    return _zip_deep(_union_fn, a, b)

        
    
ys = where
nt = exclude
