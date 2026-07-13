#!/usr/bin/env python3

from collections.abc import Callable


def spell_combiner(spell1: Callable, spell2: Callable) -> Callable:
    def combined(target: str, power: int) -> tuple:
        return (spell1(target, power), spell2(target, power))
    return combined


def power_amplifier(base_spell: Callable, multiplier: int) -> Callable:
    def amplified(target: str, power: int) -> str:
        return base_spell(target, power * multiplier)
    return amplified


def conditional_caster(condition: Callable, spell: Callable) -> Callable:
    def conditional(target: str, power: int) -> str:
        if condition(target, power):
            return spell(target, power)
        return "Spell fizzled"
    return conditional


def spell_sequence(spells: list[Callable]) -> Callable:
    def sequence(target: str, power: int) -> list:
        return [spell(target, power) for spell in spells]
    return sequence


def fireball(target: str, power: int) -> str:
    return f"Fireball hits {target} for {power}"


def heal(target: str, power: int) -> str:
    return f"Heal restores {target} for {power} HP"


def main() -> None:
    print("Testing spell combiner...")
    combined = spell_combiner(fireball, heal)
    print(combined("Dragon", 10))
    print()

    print("Testing power amplifier...")
    mega_fireball = power_amplifier(fireball, 3)
    print(f"Original: {fireball('Dragon', 10)}")
    print(f"Amplified: {mega_fireball('Dragon', 10)}")
    print()

    print("Testing conditional caster...")
    guarded = conditional_caster(lambda t, p: p >= 20, fireball)
    print(guarded("Dragon", 30))
    print(guarded("Dragon", 5))
    print()

    print("Testing spell sequence...")
    sequence = spell_sequence([fireball, heal])
    for result in sequence("Dragon", 15):
        print(result)


if __name__ == "__main__":
    main()
