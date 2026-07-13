#!/usr/bin/env python3

from ex1 import HealingCreatureFactory, TransformCreatureFactory


def main() -> None:
    print("Testing Creature with healing capability")
    healing = HealingCreatureFactory()
    print("base:")
    sproutling = healing.create_base()
    print(sproutling.describe())
    print(sproutling.attack())
    print(sproutling.heal())
    print("evolved:")
    bloomelle = healing.create_evolved()
    print(bloomelle.describe())
    print(bloomelle.attack())
    print(bloomelle.heal())
    print()
    print("Testing Creature with transform capability")
    transforming = TransformCreatureFactory()
    print("base:")
    shiftling = transforming.create_base()
    print(shiftling.describe())
    print(shiftling.attack())
    print(shiftling.transform())
    print(shiftling.attack())
    print(shiftling.revert())
    print("evolved:")
    morphagon = transforming.create_evolved()
    print(morphagon.describe())
    print(morphagon.attack())
    print(morphagon.transform())
    print(morphagon.attack())
    print(morphagon.revert())
    print()
    print("Capabilities demonstrated: heal, transform, attack and revert")


if __name__ == "__main__":
    main()
