# PhantomTrace

A Python library implementing an experimental mathematical framework where numbers can exist in two states: **present** or **absent**. It defines five operations that interact with these states in consistent, rule-based ways.

Zero is redefined: `0` is not emptiness — it's one absence (`1(0)`). This means every operation has a defined result, including division by zero.

**Read the paper**: [Absence Theory](https://www.academia.edu/150254484/Absence_Theory_Quantified_Absence_and_State_Aware_Arithmetic_within_Domains_of_Reference)

## Intellectual Property Notice

The mathematical frameworks implemented in PhantomTrace (including Absence Theory and State-Aware Arithmetic) are the subject of **US Provisional Patent Application No. 63/848,955**. While the source code is provided under the **MIT License**, the underlying methods and systems are proprietary inventions. For academic or derivative works, citation is requested as per the `CITATION.cff` file.

## Installation

```bash
pip install phantomtrace
```

## Shorthand Notation (v0.3.0)

Use the `n()` shorthand to create numbers quickly:

```python
from absence_calculator import n

n(5)       # → 5 (present)
n(5)(0)    # → 5(0) (absent) — closest to writing 5(0) directly
n(5)(1)    # → 5 (stays present)
n(3)(5)    # → 15 (multiplier — 3 × 5)
n(10)(0)   # → 10(0) (absent)

# Build vectors naturally
vec = [n(10)(0), n(20), n(30)(0), n(40), n(50)(0)]
# → [10(0), 20, 30(0), 40, 50(0)]
```

You can also use the full form: `AbsentNumber(value, absence_level)`.

## Quick Start

```python
from absence_calculator import n, add, subtract, multiply, divide, erase, format_result

# Create numbers — present (default) or absent
five = n(5)        # 5 (present)
three_absent = n(3)(0)  # 3(0) (absent)

# Addition — same state combines, mixed state is unresolved
result = add(n(5), n(3))
print(result)  # 8

# Subtraction — equal values cancel to void
result = subtract(n(7), n(7))
print(result)  # void

# Multiplication — states combine (like XOR)
result = multiply(n(5)(0), n(3))
print(result)  # 15(0)

# Erasure — flips the state of the erased portion
result = erase(n(5), n(3))
print(result)  # 2 + 3(0)

# Over-erasure — excess becomes erased debt
result = erase(n(7), n(10))
print(result)  # 7(0) + erased 3

# Resolve erased excess by adding
resolved = add(result, n(3))
print(resolved)  # 10(0)

# Division by zero — defined! (0 is one absence)
result = divide(n(10), n(1)(0))
print(result)  # 10(0)
```

## Using the Expression Solver

```python
from absence_calculator import solve, format_result

# Parse and solve string expressions
print(format_result(solve("5 + 3")))           # 8
print(format_result(solve("5(0) + 3(0)")))     # 8(0)
print(format_result(solve("7 - 7")))           # void
print(format_result(solve("5(0) * 3")))        # 15(0)
print(format_result(solve("5 erased 3")))      # 2 + 3(0)
print(format_result(solve("7 erased 10")))     # 7(0) + erased 3 (over-erasure)
print(format_result(solve("5(0)(0)")))         # 5 (double absence = present)

# Parenthesized expressions (operations on unresolved inputs)
print(format_result(solve("(1 + 5(0)) erased 1")))  # 6(0)

# Zero operations
print(format_result(solve("0 + 0")))           # 2(0) (two absences)
print(format_result(solve("0 * 0")))           # 1 (absence of absence = presence)
print(format_result(solve("10 * 0")))          # 10(0)
print(format_result(solve("10 / 0")))          # 10(0)
```

## Interactive Calculator

After installing, you can run the interactive calculator from the command line:

```bash
phantomtrace
```

Or as a Python module:

```bash
python -m absence_calculator
```

This gives you a `calc >>` prompt where you can type expressions and see results.

## Core Concepts

### Objects and States

An object is a number that has both a **value** and a **state**:
- **Present** (default): Written normally, e.g. `5`. Present quantities reflect the presence of a given unit of interest. (e.g. if the unit is a cat, then 5 represents 5 cats that are there or in a present state)
- **Absent**: Written with `(0)`, e.g. `5(0)` — think of it as `5 * 0`. Absent quantities reflect the absence of a given unit of interest. (e.g. if the unit is a phone, then 5(0) represents 5 phones that are not currently there but are still considered for computation)

Both states carry magnitude. `5` and `5(0)` both have a value of 5 — the state tells you whether it's present or absent, but the magnitude never disappears.

### Absence
  
- **Zero**: `0` is not emptiness, it's one absence (`1(0) = 1 * 0 = 0`)
- **Absence of absence** returns to present: `5(0)(0) = 5`, and `0(0) = 1`

### Operations

| Operation | Symbol | Rule |
|-----------|--------|------|
| Addition | `+` | Expands the amount of objects under consideration. Same state: magnitudes combine. Mixed: unresolved |
| Subtraction | `-` | Contracts the amount of objects under consideration. (If the domain of consideration is constricted to nothing then the result is void. Void is not an object, nor the new zero, it simply means we are not considering anything on which to act.) Same state: magnitudes reduce. Mixed: unresolved|
| Multiplication | `*` | Magnitudes multiply. States combine (present*present=present, absent*present=absent, absent*absent=present) |
| Division | `/` | Magnitudes divide. States combine same as multiplication. Division by 0 is defined! |
| Erasure | `erased` | Same state required. Remainder keeps state, erased portion flips state. Over-erasure creates erased excess |

### Over-Erasure (v0.2.0)

When you erase more than the total, the result carries an **erased excess** (erasure debt):

- `7 erased 10` = `7(0) + erased 3` — all 7 flip state, 3 excess erasure persists
- Adding resolves excess: `(7(0) + erased 3) + 3` = `10(0)`

### State Functions: `erased()` and `negative()` (v0.7.4)

Just like subtraction can be thought of as adding a negative (`x - y = x + (-y)`), erasure can be thought of as adding an erased state (`erase(x, y) = x + erased(y)`). The `erased()` function creates an erased state, and the `erase()` function is shorthand for adding that erased state.

```python
from absence_calculator import n, erase, erased, negative, add

# erased() takes one input — the number you want to apply an erased state to
erased(n(5))       # → erased 5
erased(n(5)(0))    # → erased 5(0)

# erase(x, y) is equivalent to add(x, erased(y))
# Just like subtract(x, y) is equivalent to add(x, negative(y))
erase(n(5), n(3))              # → 2 + 3(0)
add(n(5), erased(n(3)))        # → 2 + 3(0) (same thing)

# Same state + same erasure level combine when added
add(erased(n(3)), erased(n(7)))        # → erased 10
add(erased(n(3)(0)), erased(n(7)(0)))  # → erased 10(0)

# Adjacent levels resolve — erased(x) can erase x because x is there to erase
add(erased(n(5)), n(5))       # → 5(0)
add(erased(n(5)(0)), n(5)(0)) # → 5

# Two levels apart can't resolve — erased erased 5 needs erased 5, not plain 5
add(erased(erased(n(5))), n(5))        # → 5 + erased erased 5 (stays separate)
add(erased(erased(n(5))), erased(n(5)))  # → erased 5(0) (adjacent, resolves)

# negative() creates a negative number — same as normal math
negative(n(5))     # → -5
negative(n(5)(0))  # → -5(0)

# Both work on tensors element-wise
erased([n(1), n(2), n(3)])      # → [erased 1, erased 2, erased 3]
negative([n(1), n(2), n(3)])    # → [-1, -2, -3]
```

### Layered Erasure (v0.7.4)

Erasure can be layered to any depth — you can erase erased quantities from other erased quantities. The same erasure rules apply: same state required, remainder keeps state, erased portion flips state.

**Important:** Double erasure is NOT like double negatives. A double negative gives you a positive (`-(-5) = 5`). But erasing an erased number gives you the *absence* of an erased number — and that only happens when an erased number of the same kind is actually present to be erased. The absence of an erased number is its own distinct thing, not a return to the original number. Erasure and subtraction are analogous (both remove quantity), but they behave differently when layered.

Erasure can be layered to any depth. Each layer tracks its depth internally, so only quantities at the same erasure depth and same absence state can interact.

```python
from absence_calculator import n, erase, erased

# erase(erased(5), erased(3)) — erase "erased 3" from "erased 5"
# There IS an erased present number to erase, so it resolves:
# Remainder: erased 2 (unchanged)
# Erased portion: erased 3(0) — the ABSENCE of "erased 3", not a return to 3
erase(erased(n(5)), erased(n(3)))   # → erased 2 + erased 3(0)

# Full erasure — everything becomes the absence of its erased state
erase(erased(n(5)), erased(n(5)))   # → erased 5(0)

# Over-erasure — same rules apply
erase(erased(n(3)), erased(n(5)))   # → erased 3(0) + erased 2

# Works on absent-state erased quantities too
erase(erased(n(5)(0)), erased(n(3)(0)))  # → erased 2(0) + erased 3

# Mixed-state erased quantities can't erase each other
# There are no absent-state erased numbers in "erased 5" — only present-state
erase(erased(n(5)), erased(n(3)(0)))     # → erased 5 erased erased 3(0) (unresolved)

# Deeper layers work the same way — erased erased quantities erase each other
erased(erased(n(5)))                     # → erased erased 5
erased(erased(erased(n(3))))             # → erased erased erased 3

# Same depth can interact
erase(erased(erased(n(5))), erased(erased(n(3))))
# → erased erased 2 + erased erased 3(0)

# Different depths can't interact — erased erased 5 is not the same kind as erased 5
erase(erased(erased(n(5))), erased(n(5)))
# → erased erased 5 erased erased 5 (unresolved)
```

### Compound Expressions (v0.2.0)

Operations can now accept unresolved expressions as inputs:

- `(1 + 5(0)) erased 1` = `6(0)` — erases the present part, combining with the absent part

### Result Types

- **AbsentNumber**: A number with a state (present or absent)
- **Void**: Complete cancellation — not zero, but the absence of any quantity under consideration
- **ErasureResult**: Two parts — remainder (keeps state) and erased portion (flipped state)
- **ErasedExcess**: Excess erasure debt that persists until resolved. Can be created directly with `erased()`
- **Unresolved**: An expression that cannot be simplified (e.g., adding present + absent). Stores full operation data so it can be operated on in future operations

## Toggle Module

The toggle module flips states of elements in vectors, matrices, and tensors using pattern-based index selection.

### Core Toggle Operations

- `toggle.where(pattern, range, data)` — flip elements **at** pattern-computed indices
- `toggle.exclude(pattern, range, data)` — flip everything **except** pattern-computed indices
- `toggle.all(data)` — flip **every** element at any depth

The **pattern** is a function (or string expression) that's evaluated across all whole numbers. The **range** is an output filter — only results that fall within `(start, end)` become target indices. The function determines the shape of the pattern; the range determines how far it reaches.

### Vectors — Present

```python
from absence_calculator import toggle, n

# Present vector — all elements start as present
vec = [10, 20, 30, 40, 50]

# x*2 produces 0, 2, 4, 6, 8... — range (0, 4) keeps outputs 0 through 4
# Hits: indices 0, 2, 4 (the even positions)
toggle.where(lambda x: x * 2, (0, 4), vec)
# → [10(0), 20, 30(0), 40, 50(0)]    targets flipped to absent

toggle.exclude(lambda x: x * 2, (0, 4), vec)
# → [10, 20(0), 30, 40(0), 50]       non-targets flipped to absent

toggle.all(vec)
# → [10(0), 20(0), 30(0), 40(0), 50(0)]  everything flipped to absent
```

### Vectors — Absent

```python
# Absent vector — all elements start as absent
vec = [n(10)(0), n(20)(0), n(30)(0), n(40)(0), n(50)(0)]

toggle.where(lambda x: x * 2, (0, 4), vec)
# → [10, 20(0), 30, 40(0), 50]       targets flipped back to present

toggle.exclude(lambda x: x * 2, (0, 4), vec)
# → [10(0), 20, 30(0), 40, 50(0)]    non-targets flipped back to present

toggle.all(vec)
# → [10, 20, 30, 40, 50]             everything flipped back to present
```

### Vectors — Mixed

```python
# Mixed vector — some present, some absent
vec = [n(10), n(20)(0), n(30), n(40)(0), n(50)]

toggle.where(lambda x: x * 2, (0, 4), vec)
# → [10(0), 20(0), 30(0), 40(0), 50(0)]  targets flip (present→absent, absent→present)

toggle.exclude(lambda x: x * 2, (0, 4), vec)
# → [10, 20, 30, 40, 50]                  non-targets flip

toggle.all(vec)
# → [10(0), 20, 30(0), 40, 50(0)]         every element flips its state
```

### String Patterns and Single Index

```python
# String pattern — "x^2" computes target indices
toggle.where("x^2", (1, 4), [4, 7, 19, 22, 26])
# → [4, 7(0), 19, 22, 26(0)]   indices 1 (1²) and 4 (2²) toggled

# Single index — use pattern "x" with range (i, i)
toggle.where("x", (2, 2), [10, 20, 30, 40, 50])
# → [10, 20, 30(0), 40, 50]    only index 2 toggled
```

### Matrices — Present

```python
# Present matrix — toggle.all flips every element in every row
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

toggle.all(matrix)
# → [[0, 2(0), 3(0)],
#    [4(0), 5(0), 6(0)],
#    [7(0), 8(0), 9(0)]]

toggle.where("x", (0, 0), matrix)
# → [[0, 2, 3],        index 0 toggled in each row
#    [4(0), 5, 6],
#    [7(0), 8, 9]]

toggle.exclude("x", (0, 0), matrix)
# → [[1, 2(0), 3(0)],  everything except index 0 toggled
#    [4, 5(0), 6(0)],
#    [7, 8(0), 9(0)]]
```

### Matrices — Absent

```python
# Absent matrix
matrix = [[n(1)(0), n(2)(0)], [n(3)(0), n(4)(0)]]

toggle.all(matrix)
# → [[1, 2],     everything flipped back to present
#    [3, 4]]
```

### Matrices — Mixed

```python
# Mixed matrix — rows have different states
matrix = [[n(10)(0), n(20), n(30)(0)],
          [n(40), n(50)(0), n(60)]]

toggle.where("x", (1, 1), matrix)
# → [[10(0), 20(0), 30(0)],   index 1 toggled in each row
#    [40, 50, 60]]

toggle.all(matrix)
# → [[10, 20(0), 30],         every element flips
#    [40(0), 50, 60(0)]]
```

## Tensor Creation (v0.5.0)

`tensor()` creates multi-dimensional tensors — nested lists of AbsentNumbers at any depth. Vectors are rank 1, matrices are rank 2, and you can go as deep as you need. Every element always retains both its value and its state — nothing is ever removed, only toggled.

```python
from absence_calculator import tensor, n

# Vector (rank 1) — 5 elements, all absent
v = tensor(5, fill='absent')
# → [1(0), 2(0), 3(0), 4(0), 5(0)]
# Default: values are sequential — position IS identity

# Matrix (rank 2) — 3 rows of 4 elements, all present
m = tensor((3, 4), fill='present')
# → [[1, 2, 3, 4],
#    [1, 2, 3, 4],
#    [1, 2, 3, 4]]

# 3D Tensor (rank 3) — 2 matrices of 3 rows of 4 elements
t = tensor((2, 3, 4), fill='absent')
# Each element has a value and a state — absent, but never gone

# 4D Tensor (rank 4)
t4 = tensor((2, 2, 3, 5))
# Matrices inside matrices — as deep as you need
```

### Seed — State Randomization (v0.6.0)

The `seed` parameter randomizes which positions are present vs absent. Values stay sequential (position = identity) — only states change. Closer seeds produce more similar patterns, with adjacent seeds differing by exactly one position.

```python
# seed controls how many positions are present
r0 = tensor(5, seed=0)
# → [1(0), 2(0), 3(0), 4(0), 5(0)]  (seed 0 = all absent)

r3 = tensor(5, seed=3)
# → 3 positions present, 2 absent (deterministic which ones)

r4 = tensor(5, seed=4)
# → 4 positions present — differs from seed 3 by exactly 1 position

r5 = tensor(5, seed=5)
# → [1, 2, 3, 4, 5]  (seed = size = all present)

# Same seed always gives the same pattern
tensor(5, seed=3) == tensor(5, seed=3)  # True

# Wraps around: seed 6 on a size-5 tensor = seed 0
r6 = tensor(5, seed=6)
# → same as seed 0

# Works on matrices and higher — position ordering spans the entire tensor
m = tensor((3, 4), seed=6)
# 6 of 12 positions are present, rest absent
```

### Inspecting Tensors

```python
toggle.rank(n(5))                       # → 0 (scalar)
toggle.rank([n(1), n(2)])               # → 1 (vector)
toggle.rank([[n(1), n(2)], [n(3), n(4)]])  # → 2 (matrix)
toggle.rank(tensor((2, 3, 4)))          # → 3 (3D tensor)

toggle.shape(tensor((3, 4)))            # → (3, 4)
toggle.shape(tensor((2, 3, 4)))         # → (2, 3, 4)
```

## Tensor Operations (v0.7.0)

All calculator operations now work on tensors — add, subtract, multiply, divide, and erase. Both inputs must have the same shape. Operations are applied element-by-element at every depth. Each position follows its own rules, so some positions may be unresolved while others resolve cleanly.

### All Operations on Tensors

```python
from absence_calculator import n, add, subtract, multiply, divide, erase

# Addition — same state combines, mixed is unresolved
add([n(7), n(8)(0), n(10)], [n(4), n(3), n(7)(0)])
# → [11, 8(0) + 3, 10 + 7(0)]

# Subtraction — equal values cancel to void
subtract([n(7), n(5), n(10)(0)], [n(3), n(5), n(4)(0)])
# → [4, void, 6(0)]

# Multiplication — states combine (absent × absent = present)
multiply([n(3), n(4)(0), n(2)(0)], [n(5), n(3), n(6)(0)])
# → [15, 12(0), 12]

# Division — magnitudes divide, states combine
divide([n(10), n(9)(0), n(8)], [n(2), n(3)(0), n(4)])
# → [5, 3, 2]

# Erasure — flips state of erased portion
erase([n(7), n(5), n(3)], [n(3), n(5), n(1)])
# → [4 + 3(0), 5(0), 2 + 0]

# Erasure with unresolved elements
erase([n(7), add(n(5), n(3)(0)), n(3)], [n(6), n(4), n(2)])
# → [1 + 6(0), 1 + 7(0), 1 + 2(0)]

# All operations work on matrices and higher-rank tensors too
add([[n(1), n(2)], [n(3), n(4)]], [[n(5), n(6)], [n(7), n(8)]])
# → [[6, 8], [10, 12]]
```

### Combine (v0.5.0, updated v0.6.0)

`combine()` counts present vs absent at each position, ignoring scalar values. Each element becomes `1` (if present) or `1(0)` (if absent), then adds them together. Void elements contribute nothing — they're not present or absent, just void. Two voids combine to void.

```python
from absence_calculator import n, combine, VOID

# Mixed states — each position has one present and one absent
combine([n(1), n(2)(0), n(3), n(4)(0)],
        [n(0), n(2), n(3)(0), n(4)])
# → [1 + 0, 0 + 1, 1 + 0, 0 + 1]
# (0 here is 1(0) — one absence)

# Both present at every position
combine([n(5), n(3)], [n(2), n(7)])
# → [2, 2]    (two presents each)

# Both absent at every position
combine([n(5)(0), n(3)(0)], [n(2)(0), n(7)(0)])
# → [2(0), 2(0)]    (two absents each)

# Combine with void — counts only the non-void side (v0.6.0)
combine([n(5), n(4)(0), n(3), n(2)(0)], [VOID, VOID, VOID, VOID])
# → [1, 0, 1, 0]
# Present → 1, Absent → 1(0) (displayed as 0), Void contributes nothing

# Void + void = void
combine([VOID, VOID], [VOID, VOID])
# → [void, void]
```

### Compare (v0.5.0)

`compare()` measures the shift in present vs absent from tensor 1 to tensor 2. Most useful on already-combined tensors where each position has the same total magnitude split between present and absent.

Works directly with combine output — no need to manually construct Unresolved expressions:

```python
from absence_calculator import n, combine, compare

# Two pairs of tensors with different state patterns
c1 = [n(1), n(2), n(3), n(4)(0)]     # P P P A
c2 = [n(5), n(6), n(7), n(8)]        # P P P P
state1 = combine(c1, c2)
# → [2, 2, 2, 0 + 1]  (2P, 2P, 2P, 1A+1P)

c3 = [n(1)(0), n(2), n(3)(0), n(4)]  # A P A P
c4 = [n(5), n(6)(0), n(7)(0), n(8)]  # P A A P
state2 = combine(c3, c4)
# → [0 + 1, 1 + 0, 2(0), 2]  (1A+1P, 1P+1A, 2A, 2P)

compare(state1, state2)
# → [0, 0, 2(0), 1]
# Position 0: 2 present → 1 present = lost 1 → 0 (which is 1(0))
# Position 1: 2 present → 1 present = lost 1 → 0 (which is 1(0))
# Position 2: 2 present → 0 present = lost 2 → 2(0)
# Position 3: 1 present → 2 present = gained 1 → 1

# No change returns void
same1 = combine([n(1), n(2)(0)], [n(3)(0), n(4)])  # 1+0, 1+0
same2 = combine([n(5)(0), n(6)], [n(7), n(8)(0)])  # 1+0, 1+0
compare(same1, same2)
# → [void, void]  (no shift at either position)
```

## Trace Function (v0.7.0)

`trace()` is an absent-aware lambda — it evaluates a function over a range of values, producing a vector of results. The range can be present or absent, and all operations work naturally within the trace. Think of it as "map a function across a range of AbsentNumbers."

### Absent Number Ordering in Ranges

Absent numbers are considered "smaller" than present numbers. The ordering goes:

```
... 3(0), 2(0), 1(0), 1, 2, 3 ...
```

This means a range can cross from absent to present naturally:

```python
from absence_calculator import n, trace

# Range from 3(0) to 3 covers: 3(0), 2(0), 1(0), 1, 2, 3
trace(lambda x: x, n(3)(0), n(3))
# → [3(0), 2(0), 1(0), 1, 2, 3]

# Range from 500(0) to 7 covers all absent values down, then present up
trace(lambda x: x, n(500)(0), n(7))
# → [500(0), 499(0), ... 1(0), 1, 2, ... 7]  (507 elements)

# Reverse: 3 down to 3(0) goes present to absent
trace(lambda x: x, n(3), n(3)(0))
# → [3, 2, 1, 1(0), 2(0), 3(0)]
```

### Basic Traces

```python
from absence_calculator import n, trace, multiply, add, erase, divide, subtract

# x² over an absent range: 5(0) down to 2(0)
trace(lambda x: multiply(x, x), n(5)(0), n(2)(0))
# → [25, 16, 9, 4]
# 5(0)*5(0) = 25 (absent × absent = present)

# x erased x — a "toggler" that flips every value
trace(lambda x: erase(x, x), n(1), n(5))
# → [1(0), 2(0), 3(0), 4(0), 5(0)]

# Cross-state range with erasure
trace(lambda x: erase(x, n(5)(0)), n(5)(0), n(6))
# → [5, 4 + erased 1, ... 1 + erased 4, 1 + erased 5(0), ... 6 + erased 5(0)]
# Absent values erase same-state, present values create unresolved erasure debt

# x + x over a present range
trace(lambda x: add(x, x), n(1), n(4))
# → [2, 4, 6, 8]

# x - 1 over a range
trace(lambda x: subtract(x, n(1)), n(3), n(5))
# → [2, 3, 4]

# x / 2 over a range
trace(lambda x: divide(x, n(2)), n(2), n(6))
# → [1, 1.5, 2, 2.5, 3]

# Mixed operations: x² + x over absent range
trace(lambda x: add(multiply(x, x), x), n(1)(0), n(3)(0))
# → [1 + 0, 4 + 2(0), 9 + 3(0)]
# x² is present (absent × absent), x is absent → unresolved at each position
```

### Unbound and Partial Traces

You can create a trace without specifying the range, and bind it later. `bind()` returns a new result — it doesn't modify the original trace.

```python
# Unbound — define the function now, bind the range later
t = trace(lambda x: multiply(x, x))
print(t)             # trace(unbound)
t(n(5))              # → 25 (call it like a function)
result = t.bind(n(1), n(5))  # → [1, 4, 9, 16, 25]

# Partially bound — set start now, end later
t2 = trace(lambda x: add(x, n(10)), start=n(1))
print(t2)            # trace(start=1)
result = t2.bind(n(3))   # → [11, 12, 13]  (fills in the missing end)

# Or use keyword args
result = t2.bind(end=n(3))   # → [11, 12, 13]
```

### Void Rejection

Trace rejects void ranges — void means "no calculation":

```python
from absence_calculator import VOID

trace(lambda x: x, VOID, n(5))
# → ValueError: Cannot trace over void — void is no calculation
```

## Toggle Module

The toggle module flips states of elements in vectors, matrices, and tensors using pattern-based index selection.

### Toggling at Any Depth

`toggle.all()` works at every depth — flips every element regardless of how deeply nested:

```python
from absence_calculator import tensor, toggle

# All works on vectors, matrices, tensors, anything
t = tensor((2, 3, 4), fill='present')
t_flipped = toggle.all(t)
# Every element in the entire 2×3×4 structure is now absent
# Values preserved — only states changed
```

### Axis-Aware Toggling (v0.4.0)

`where()` and `exclude()` now accept an `axis` parameter to control which level toggling happens at:

```python
# Matrix 3×5, all absent
m = tensor((3, 5), fill='absent')

# Identity function, range (0, 2) — keeps outputs 0, 1, 2
result = toggle.where(lambda x: x, (0, 2), m, axis=-1)
# Row 0: P P P _ _
# Row 1: P P P _ _
# Row 2: P P P _ _

# x*2, range (0, 4) — keeps outputs 0 through 4, hits 0, 2, 4
result = toggle.where(lambda x: x * 2, (0, 4), m, axis=-1)
# Row 0: P _ P _ P
# Row 1: P _ P _ P
# Row 2: P _ P _ P
# Even indices only — the pattern controls the shape, the range controls the reach

# 3D tensor — toggling reaches the deepest vectors
t = tensor((2, 2, 4), fill='absent')
result = toggle.where(lambda x: x, (1, 2), t, axis=-1)
# Outputs in [1,2] → toggles indices 1 and 2 in every vector:
# [0][0]: _ P P _
# [0][1]: _ P P _
# [1][0]: _ P P _
# [1][1]: _ P P _
```

### Selecting Slices

`toggle.select()` pulls out a sub-structure along any axis. The result is still a valid tensor — one rank lower:

```python
m = [[n(1), n(2), n(3)],
     [n(4), n(5), n(6)],
     [n(7), n(8), n(9)]]

# Select row 1 (axis=0) — gives a vector
toggle.select(m, axis=0, index=1)
# → [4, 5, 6]

# Select column 2 (axis=1) — gives a vector
toggle.select(m, axis=1, index=2)
# → [3, 6, 9]

# 3D tensor — selecting axis=0 gives a matrix
t = [[[n(1), n(2)], [n(3), n(4)]],
     [[n(5), n(6)], [n(7), n(8)]]]
toggle.select(t, axis=0, index=0)
# → [[1, 2], [3, 4]]

# Selecting axis=2 gives a matrix of single values
toggle.select(t, axis=2, index=1)
# → [[2, 4], [6, 8]]
```

### Replacing Slices

`toggle.assign()` replaces a slice at a given position:

```python
m = [[n(1), n(2)], [n(3), n(4)]]
new_row = [n(10), n(20)]

result = toggle.assign(m, axis=0, index=0, value=new_row)
# → [[10, 20], [3, 4]]   row 0 replaced, row 1 unchanged
```

### Combining Across an Axis

`toggle.across()` applies a function element-by-element across one axis, combining sub-structures. Each result is still an AbsentNumber with its value and state:

```python
m = [[n(1), n(2)(0), n(3)],     # Row 0: P _ P
     [n(1)(0), n(2), n(3)]]     # Row 1: _ P P

def both_present(x, y):
    if x.is_present and y.is_present:
        return n(x.value)
    return n(x.value)(0)

toggle.across(m, axis=0, fn=both_present)
# → [1(0), 2(0), 3]
# Only index 2 is present in both rows
# Values and states preserved — nothing removed
```

### Counting

```python
v = [n(1), n(2), n(3)(0), n(4), n(5)(0)]
toggle.count_present(v)           # → 3 (three elements are present)

m = [[n(1), n(2)(0)], [n(3)(0), n(4)]]
toggle.count_present(m)           # → 2 (two elements present total)

toggle.present_indices(v)         # → [0, 1, 3] (which positions are present)
```

### Intersect and Union (Convenience)

Shorthand for common `across()` patterns — both preserve all values and states:

```python
a = [n(1), n(2), n(3)(0), n(4),    n(5)(0)]  # P P _ P _
b = [n(1), n(2)(0), n(3), n(4)(0), n(5)(0)]  # P _ P _ _

toggle.intersect(a, b)  # → P _ _ _ _  (present only where BOTH are present)
toggle.union(a, b)      # → P P P P _  (present where EITHER is present)

# These work at any depth — matrices, 3D tensors, etc.
# Equivalent to across() with AND/OR logic functions
```

### Backward Compatibility

`toggle.ys` = `toggle.where`, `toggle.nt` = `toggle.exclude` — old names still work.

All existing vector and matrix code works unchanged. The `axis` parameter defaults to `-1` (last axis), which matches the original behavior.

## API Reference

### Types

- `AbsentNumber(value, absence_level=0)` — A number with a state. `absence_level` 0 = present, 1 = absent. Callable: `num(0)` flips state, `num(1)` keeps state, `num(k)` multiplies
- `n(value, absence_level=0)` — Shorthand for creating AbsentNumbers: `n(5)` = present 5, `n(5)(0)` = absent 5
- `Void` / `VOID` — Represents complete cancellation
- `ErasureResult(remainder, erased)` — Result of an erasure operation
- `ErasedExcess(value, absence_level=0)` — Excess erasure debt from over-erasure
- `Unresolved(left, op, right)` — An expression that can't be simplified

### Calculator Functions (all tensor-aware since v0.7.0)

- `add(x, y)` — Add two values or tensors element-wise (supports compound inputs with excess resolution)
- `subtract(x, y)` — Subtract two values or tensors element-wise
- `multiply(x, y)` — Multiply two values or tensors element-wise
- `divide(x, y)` — Divide two values or tensors element-wise
- `erase(x, y)` — Erase y from x, element-wise on tensors (supports over-erasure and compound inputs)
- `solve(expr_string)` — Parse and evaluate a string expression (supports parentheses)
- `format_result(result)` — Convert any result (including tensors) to a readable string
- `parse_number(s)` — Parse a string like `"5(0)"` into an AbsentNumber

### Special Functions (v0.5.0, updated v0.6.0)

- `combine(x, y)` — Count present vs absent at each position (ignores scalar values, returns state counts). Void contributes nothing; void + void = void
- `compare(x, y)` — Measure the shift in present vs absent from tensor 1 to tensor 2

### Trace Function (v0.7.0)

- `trace(fn, start=None, end=None)` — Evaluate a function over a range of AbsentNumbers, producing a vector. Supports unbound/partial binding via `.bind()`. Rejects void ranges

### Tensor Creation (v0.5.0, updated v0.6.0)

- `tensor(shape, fill='absent', seed=None)` — Create a tensor of any shape. Sequential values by default. Seed randomizes present/absent states (not values) — adjacent seeds differ by one position

### Toggle — Core

- `toggle.where(pattern, range, data, axis=-1)` — Toggle elements at pattern-computed indices along a specific axis
- `toggle.exclude(pattern, range, data, axis=-1)` — Toggle all elements NOT at pattern-computed indices along a specific axis
- `toggle.all(data)` — Flip the state of every element at any depth

### Toggle — Tensor Inspection

- `toggle.rank(data)` — Detect depth of nesting (0=scalar, 1=vector, 2=matrix, 3+=tensor)
- `toggle.shape(data)` — Return dimensions as a tuple
- `toggle.select(data, axis, index)` — Extract a slice along an axis (result is one rank lower)
- `toggle.assign(data, axis, index, value)` — Replace a slice at a given position
- `toggle.across(data, axis, fn)` — Combine elements across an axis using a function
- `toggle.count_present(data, axis=None)` — Count present elements (total or along an axis)
- `toggle.present_indices(vector)` — Return which positions are present in a vector
- `toggle.intersect(a, b)` — Present only where both inputs are present (convenience for across with AND)
- `toggle.union(a, b)` — Present where either input is present (convenience for across with OR)
- `toggle.ys` / `toggle.nt` — Backward-compatible aliases for `where` / `exclude`

### Constants

- `ALL_OPERATIONS` — Dictionary describing all operations with rules and examples

## License

MIT
