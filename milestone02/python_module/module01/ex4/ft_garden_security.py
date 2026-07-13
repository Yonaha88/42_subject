#!/usr/bin/env python3

class Plant:
    def __init__(self, name: str, height: float, days: int) -> None:
        self.name = name
        self._height = 0.0
        self._age = 0
        self.set_height(height)
        self.set_age(days)

    def show(self) -> None:
        print(f"{self.name}: {round(self._height, 1)}cm, {self._age} days old")

    def grow(self) -> None:
        self._height += 0.8

    def age(self) -> None:
        self._age += 1

    def set_height(self, height: float) -> None:
        if height < 0:
            print(f"{self.name}: Error, height can't be negative")
            print("Height update rejected")
        else:
            self._height = height

    def set_age(self, age: int) -> None:
        if age < 0:
            print(f"{self.name}: Error, age can't be negative")
            print("Age update rejected")
        else:
            self._age = age

    def get_height(self) -> float:
        return self._height

    def get_age(self) -> int:
        return self._age


def ft_garden_security() -> None:
    print("=== Garden Security System ===")
    plant = Plant("Rose", 15.0, 10)
    print("Plant created: ", end="")
    plant.show()
    print()
    plant.set_height(25.0)
    print("Height updated: 25cm")
    plant.set_age(30)
    print("Age updated: 30 days")
    print()
    plant.set_height(-5.0)
    plant.set_age(-1)
    print()
    print("Current state: ", end="")
    plant.show()


if __name__ == "__main__":
    ft_garden_security()
