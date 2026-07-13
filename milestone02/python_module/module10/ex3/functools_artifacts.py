#!/usr/bin/env python3

import functools
import operator
from collections.abc import Callable
from typing import Any


def spell_reducer(spells: list[int], operation: str) -> int:
    if not spells:
        return 0
    operations: dict[str, Callable] = {
        "add": operator.add,
        "multiply": operator.mul,
        "max": max,
        "min": min,
    }
    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}")
    return functools.reduce(operations[operation], spells)


def partial_enchanter(base_enchantment: Callable) -> dict[str, Callable]:
    return {
        "fire": functools.partial(base_enchantment, 50, "fire"),
        "water": functools.partial(base_enchantment, 50, "water"),
        "earth": functools.partial(base_enchantment, 50, "earth"),
    }


@functools.lru_cache(maxsize=None)
def memoized_fibonacci(n: int) -> int:
    if n < 2:
        return n
    return memoized_fibonacci(n - 1) + memoized_fibonacci(n - 2)


def spell_dispatcher() -> Callable[[Any], str]:
    @functools.singledispatch
    def dispatch(spell: Any) -> str:
        return "Unknown spell type"

    @dispatch.register
    def _(spell: int) -> str:
        return f"{spell} damage"

    @dispatch.register
    def _(spell: str) -> str:
        return spell

    @dispatch.register
    def _(spell: list) -> str:
        return f"{len(spell)} spells"

    return dispatch


def base_enchantment(power: int, element: str, target: str) -> str:
    return f"{element.capitalize()} enchantment (power {power}) on {target}"


def main() -> None:
    print("Testing spell reducer...")
    print(f"Sum: {spell_reducer([10, 20, 30, 40], 'add')}")
    print(f"Product: {spell_reducer([10, 20, 30, 40], 'multiply')}")
    print(f"Max: {spell_reducer([10, 20, 30, 40], 'max')}")
    print(f"Empty: {spell_reducer([], 'add')}")
    print()

    print("Testing partial enchanter...")
    enchanters = partial_enchanter(base_enchantment)
    print(enchanters["fire"]("Sword"))
    print(enchanters["water"]("Shield"))
    print()

    print("Testing memoized fibonacci...")
    print(f"Fib(0): {memoized_fibonacci(0)}")
    print(f"Fib(1): {memoized_fibonacci(1)}")
    print(f"Fib(10): {memoized_fibonacci(10)}")
    print(f"Fib(15): {memoized_fibonacci(15)}")
    print(f"Cache: {memoized_fibonacci.cache_info()}")
    print()

    print("Testing spell dispatcher...")
    cast = spell_dispatcher()
    print(f"Damage spell: {cast(42)}")
    print(f"Enchantment: {cast('fireball')}")
    print(f"Multi-cast: {cast(['a', 'b', 'c'])}")
    print(cast(3.14))


if __name__ == "__main__":
    main()
