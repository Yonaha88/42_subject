#!/usr/bin/env python3

class Plant:
    def __init__(self, name: str, height: float, days: int) -> None:
        self.name = name
        self.height = height
        self.days = days

    def show(self) -> None:
        print(f"{self.name}: {round(self.height, 1)}cm, {self.days} days old")

    def grow(self) -> None:
        self.height += 0.8

    def age(self) -> None:
        self.days += 1


def ft_plant_factory() -> None:
    rose = Plant("Rose", 25.0, 30)
    oak = Plant("Oak", 200.0, 365)
    cactus = Plant("Cactus", 5.0, 90)
    sunflower = Plant("Sunflower", 80.0, 45)
    fern = Plant("Fern", 15.0, 120)
    print("=== Plant Factory Output ===")
    print("Created:", end=' ')
    rose.show()
    print("Created:", end=' ')
    oak.show()
    print("Created:", end=' ')
    cactus.show()
    print("Created:", end=' ')
    sunflower.show()
    print("Created:", end=' ')
    fern.show()


if __name__ == "__main__":
    ft_plant_factory()
