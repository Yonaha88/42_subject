#!/usr/bin/env python3

from ex0 import AquaFactory, CreatureFactory, FlameFactory


def test_factory(factory: CreatureFactory) -> None:
    print("Testing factory")
    base = factory.create_base()
    print(base.describe())
    print(base.attack())
    evolved = factory.create_evolved()
    print(evolved.describe())
    print(evolved.attack())
    print()


def test_battle(first: CreatureFactory, second: CreatureFactory) -> None:
    print("Testing battle")
    one = first.create_base()
    two = second.create_base()
    print(one.describe())
    print("vs.")
    print(two.describe())
    print("fight!")
    print(one.attack())
    print(two.attack())


def main() -> None:
    flame = FlameFactory()
    aqua = AquaFactory()
    test_factory(flame)
    test_factory(aqua)
    test_battle(flame, aqua)


if __name__ == "__main__":
    main()
