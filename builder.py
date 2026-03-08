class State:
    def __init__(self, name, space):
        self.name = name
        self.space = space

    def __repr__(self):
        return f"State({self.name!r})"

    def __eq__(self, other):
        if isinstance(other, State):
            return self.name == other.name and self.space is other.space
        return False

    def __hash__(self):
        return hash((self.name, id(self.space)))


class StateNumber:
    def __init__(self, value, state):
        self.value = value
        self.state = state

    def __repr__(self):
        return f"{self.value}[{self.state.name}]"

    def __eq__(self, other):
        if isinstance(other, StateNumber):
            return self.value == other.value and self.state == other.state
        return False


class StateTransition:
    def __init__(self, name, from_state, to_state, space):
        self.name = name
        self.from_state = from_state
        self.to_state = to_state
        self.space = space

    def __repr__(self):
        return f"StateTransition({self.name!r}, {self.from_state.name} -> {self.to_state.name})"

    def __eq__(self, other):
        if isinstance(other, StateTransition):
            return (self.name == other.name and
                    self.from_state == other.from_state and
                    self.to_state == other.to_state)
        return False


class UnresolvedStateOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"

    def __eq__(self, other):
        if isinstance(other, UnresolvedStateOp):
            return self.left == other.left and self.op == other.op and self.right == other.right
        return False


class StateRule:
    def __init__(self, operation, same_state="combine", mixed_state="unresolved", state_combination=None):
        self.operation = operation
        self.same_state = same_state
        self.mixed_state = mixed_state
        self.state_combination = state_combination or {}

    def __repr__(self):
        return f"StateRule({self.operation!r})"


class _BuilderEndpoint:
    def __init__(self, state_name, size):
        self.state_name = state_name
        self.size = size

    def __repr__(self):
        return f"{self.size}({self.state_name})"


class _BuilderOrdering:
    def __init__(self, name, endpoints):
        self.name = name
        self.endpoints = endpoints
        self.state_sequence = [ep.state_name for ep in endpoints]

    def __repr__(self):
        return f"ordering({self.name!r}, {self.endpoints})"


class StateSpace:
    def __init__(self, name):
        self.name = name
        self._states = {}
        self._transitions = {}
        self._rules = {}
        self._orderings = {}

    def add_state(self, name):
        state = State(name, self)
        self._states[name] = state
        return state

    def get_state(self, name):
        if name not in self._states:
            raise ValueError(f"Unknown state: {name!r} in space {self.name!r}")
        return self._states[name]

    def add_transition(self, name, from_state, to_state):
        if isinstance(from_state, str):
            from_state = self.get_state(from_state)
        if isinstance(to_state, str):
            to_state = self.get_state(to_state)
        transition = StateTransition(name, from_state, to_state, self)
        self._transitions[name] = transition
        return transition

    def add_rule(self, operation, same_state="combine", mixed_state="unresolved", state_combination=None):
        resolved_combination = {}
        if state_combination:
            for (s1, s2), result in state_combination.items():
                k1 = s1 if isinstance(s1, str) else s1.name
                k2 = s2 if isinstance(s2, str) else s2.name
                r = result if isinstance(result, str) else result.name
                resolved_combination[(k1, k2)] = r
        rule = StateRule(operation, same_state, mixed_state, resolved_combination)
        self._rules[operation] = rule
        return rule

    def number(self, value, state):
        if isinstance(state, str):
            state = self.get_state(state)
        return StateNumber(value, state)

    def _apply_op(self, op_name, x, y, value_fn):
        if not isinstance(x, StateNumber) or not isinstance(y, StateNumber):
            raise TypeError(f"Both operands must be StateNumber instances")

        result_value = value_fn(x.value, y.value)

        rule = self._rules.get(op_name)

        if rule:
            combo = rule.state_combination
            key = (x.state.name, y.state.name)
            if key in combo:
                result_state = self.get_state(combo[key])
                return StateNumber(result_value, result_state)

        if x.state == y.state:
            if rule and rule.same_state == "combine":
                return StateNumber(result_value, x.state)
            elif rule and rule.same_state == "unresolved":
                return UnresolvedStateOp(x, op_name, y)
            return StateNumber(result_value, x.state)

        if rule and rule.mixed_state == "unresolved":
            return UnresolvedStateOp(x, op_name, y)

        return UnresolvedStateOp(x, op_name, y)

    def add(self, x, y):
        return self._apply_op("add", x, y, lambda a, b: a + b)

    def subtract(self, x, y):
        return self._apply_op("subtract", x, y, lambda a, b: a - b)

    def multiply(self, x, y):
        return self._apply_op("multiply", x, y, lambda a, b: a * b)

    def divide(self, x, y):
        return self._apply_op("divide", x, y, lambda a, b: a / b if b != 0 else None)

    def transition(self, name, number):
        if name not in self._transitions:
            raise ValueError(f"Unknown transition: {name!r} in space {self.name!r}")
        t = self._transitions[name]
        if not isinstance(number, StateNumber):
            raise TypeError(f"Can only transition StateNumber instances")
        if number.state != t.from_state:
            raise ValueError(
                f"Transition {name!r} requires state {t.from_state.name!r}, "
                f"got {number.state.name!r}"
            )
        return StateNumber(number.value, t.to_state)

    @property
    def states(self):
        return dict(self._states)

    @property
    def transitions(self):
        return dict(self._transitions)

    @property
    def rules(self):
        return dict(self._rules)

    def largest(self, state_name):
        if state_name not in self._states:
            raise ValueError(f"Unknown state: {state_name!r} in space {self.name!r}")
        return _BuilderEndpoint(state_name, "largest")

    def smallest(self, state_name):
        if state_name not in self._states:
            raise ValueError(f"Unknown state: {state_name!r} in space {self.name!r}")
        return _BuilderEndpoint(state_name, "smallest")

    def ordering(self, name, endpoints):
        seen = set()
        for ep in endpoints:
            if ep.state_name in seen:
                raise ValueError(f"Duplicate state in ordering: {ep.state_name!r}")
            if ep.state_name not in self._states:
                raise ValueError(f"Unknown state: {ep.state_name!r} in space {self.name!r}")
            seen.add(ep.state_name)
        o = _BuilderOrdering(name, endpoints)
        self._orderings[name] = o
        return o

    def trace(self, fn, start, end, order=None):
        if not isinstance(start, StateNumber) or not isinstance(end, StateNumber):
            raise TypeError("trace start and end must be StateNumber instances")

        if start.state == end.state:
            step = 1 if end.value >= start.value else -1
            results = []
            current = start.value
            target = end.value
            while (step > 0 and current <= target) or (step < 0 and current >= target):
                results.append(fn(StateNumber(current, start.state)))
                current += step
            return results

        if order is None:
            raise ValueError(
                "Cannot trace between different states without an ordering. "
                "Use: space.ordering('name', [space.largest('state1'), space.largest('state2')])"
            )

        if isinstance(order, str):
            if order not in self._orderings:
                raise ValueError(f"Unknown ordering: {order!r} in space {self.name!r}")
            order = self._orderings[order]

        start_state = start.state.name
        end_state = end.state.name
        seq = order.state_sequence

        start_idx = seq.index(start_state) if start_state in seq else -1
        end_idx = seq.index(end_state) if end_state in seq else -1
        if start_idx < 0 or end_idx < 0:
            raise ValueError("Start/end states not found in ordering")

        forward = start_idx < end_idx

        if forward:
            state_order = seq[start_idx:end_idx + 1]
        else:
            state_order = list(reversed(seq[end_idx:start_idx + 1]))

        results = []
        for i, sname in enumerate(state_order):
            state = self._states[sname]
            if i == 0:
                lo, hi = 1, start.value
                vals = list(range(start.value, 0, -1))
            elif i == len(state_order) - 1:
                vals = list(range(1, end.value + 1))
            else:
                ep = next((e for e in order.endpoints if e.state_name == sname), None)
                if ep and ep.size == "largest":
                    vals = list(range(1, 2))
                else:
                    vals = [1]
            for v in vals:
                results.append(fn(StateNumber(v, state)))

        if not forward:
            results.reverse()

        return results

    def __repr__(self):
        return f"StateSpace({self.name!r}, states={list(self._states.keys())})"


def presence_absence_space():
    space = StateSpace("presence_absence")

    present = space.add_state("present")
    absent = space.add_state("absent")

    space.add_transition("absence", present, absent)
    space.add_transition("presence", absent, present)

    space.add_rule("add", same_state="combine", mixed_state="unresolved")
    space.add_rule("subtract", same_state="combine", mixed_state="unresolved")
    space.add_rule("multiply", same_state="combine", mixed_state="unresolved",
                   state_combination={
                       ("present", "present"): "present",
                       ("present", "absent"): "absent",
                       ("absent", "present"): "absent",
                       ("absent", "absent"): "present",
                   })
    space.add_rule("divide", same_state="combine", mixed_state="unresolved",
                   state_combination={
                       ("present", "present"): "present",
                       ("present", "absent"): "absent",
                       ("absent", "present"): "absent",
                       ("absent", "absent"): "present",
                   })

    return space
