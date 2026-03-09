"""
Game of 24 solver — core algorithm (Python translation of index.html solver)

Usage:
    python3 solver.py 4 9 0 7
    python3 solver.py 3 3 8 8
"""

import sys
import math
from itertools import combinations

FACT = [1, 1, 2, 6, 24, 120, 720, 5040]  # 0! .. 7!
EPS  = 1e-9


def expand_unary(val: float, expr: str, max_depth: int = 2) -> list[tuple[float, str]]:
    """All values reachable from (val, expr) via chained √ and ! up to max_depth.
    Works on any (val, expr) pair — used both for bare digits and combined results."""
    queue = [(val, expr, 0)]
    seen  = {val}
    out   = []

    while queue:
        v, e, d = queue.pop(0)
        out.append((v, e))
        if d >= max_depth:
            continue

        # Factorial (must change the value)
        if float(v).is_integer() and 0 <= v <= 7 and FACT[int(v)] != v:
            f = FACT[int(v)]
            if f not in seen:
                seen.add(f)
                fe = f"{e}!" if e.startswith("(") else f"({e})!"
                queue.append((f, fe, d + 1))

        # Square root (perfect squares > 1)
        if v > 1 and float(v).is_integer():
            s = round(math.sqrt(v))
            if s * s == v and s not in seen:
                seen.add(s)
                queue.append((s, f"√({e})", d + 1))

    return out


def pre_expand(n: int) -> list[tuple[float, str]]:
    """All values reachable from digit n via chained √ and ! (depth ≤ 2)."""
    return expand_unary(n, str(n))


def combine(a: tuple, b: tuple) -> list[tuple[float, str]]:
    """All results of one binary operation on (a, b)."""
    av, ae = a
    bv, be = b
    if not (math.isfinite(av) and math.isfinite(bv)):
        return []

    results = [
        (av + bv, f"({ae}+{be})"),
        (av - bv, f"({ae}-{be})"),
        (av * bv, f"({ae}×{be})"),
    ]

    if abs(bv) > EPS:
        results.append((av / bv, f"({ae}÷{be})"))
        # Integer mod: positive divisor only
        if bv > 0 and float(av).is_integer() and float(bv).is_integer():
            results.append((av % bv, f"({ae} mod {be})"))

    # Power: small non-negative integer exponent only
    if float(bv).is_integer() and 0 <= bv <= 5:
        p = av ** bv
        if math.isfinite(p) and abs(p) < 100_000:
            results.append((p, f"({ae}^{be})"))

    return [(v, e) for v, e in results if math.isfinite(v) and abs(v) < 1e7]


def expand_unary(val: float, expr: str, max_depth: int = 2) -> list[tuple[float, str]]:
    """All values reachable from (val, expr) via chained √ and ! up to max_depth.
    Same BFS as pre_expand but works on any (val, expr) pair, not just bare digits."""
    queue = [(val, expr, 0)]
    seen  = {val}
    out   = []

    while queue:
        v, e, d = queue.pop(0)
        out.append((v, e))
        if d >= max_depth:
            continue

        # Factorial (must change the value)
        if float(v).is_integer() and 0 <= v <= 7 and FACT[int(v)] != v:
            f = FACT[int(v)]
            if f not in seen:
                seen.add(f)
                fe = f"{e}!" if e.startswith("(") else f"({e})!"
                queue.append((f, fe, d + 1))

        # Square root (perfect squares > 1)
        if v > 1 and float(v).is_integer():
            s = round(math.sqrt(v))
            if s * s == v and s not in seen:
                seen.add(s)
                queue.append((s, f"√({e})", d + 1))

    return out


def strip_outer(expr: str) -> str:
    """Remove redundant outermost parentheses."""
    while expr.startswith("(") and expr.endswith(")"):
        depth, full = 0, True
        for i in range(len(expr) - 1):
            if expr[i] == "(":   depth += 1
            elif expr[i] == ")": depth -= 1
            if depth == 0:
                full = False
                break
        if full:
            expr = expr[1:-1]
        else:
            break
    return expr


def solve_flat(pool, target, solutions, seen, max_sols):
    """Recursive solver on a flat pool of (val, expr) pairs."""
    if len(solutions) >= max_sols:
        return

    if len(pool) == 1:
        val, expr = pool[0]
        if abs(val - target) < EPS:
            key = expr.replace(" ", "")
            if key not in seen:
                seen.add(key)
                solutions.append(strip_outer(expr))
        return

    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            if len(solutions) >= max_sols:
                return
            rest  = [x for k, x in enumerate(pool) if k != i and k != j]
            pairs = combine(pool[i], pool[j]) + combine(pool[j], pool[i])

            for c in pairs:
                # Try c directly, then all values reachable from c via √ and !
                for u in expand_unary(*c):
                    solve_flat(rest + [u], target, solutions, seen, max_sols)
                    if len(solutions) >= max_sols:
                        return


def find_solutions(numbers: list[int], target=24, max_sols=3) -> list[str]:
    """Main entry point: returns up to max_sols expression strings."""
    solutions, seen = [], set()
    expanded = [pre_expand(n) for n in numbers]

    def go(idx, current):
        if len(solutions) >= max_sols:
            return
        if idx == len(expanded):
            solve_flat(current, target, solutions, seen, max_sols)
            return
        for item in expanded[idx]:
            go(idx + 1, current + [item])
            if len(solutions) >= max_sols:
                return

    go(0, [])
    return solutions


# ── CLI ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 solver.py <d1> <d2> <d3> <d4>")
        sys.exit(1)

    nums = [int(x) for x in sys.argv[1:]]
    sols = find_solutions(nums)

    if sols:
        for i, s in enumerate(sols, 1):
            print(f"  {i}. {s} = 24")
    else:
        print(f"  No solution for {nums} (even with √ and !)")
