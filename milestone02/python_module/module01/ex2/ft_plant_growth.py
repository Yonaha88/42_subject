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


def ft_plant_growth() -> None:
    rose = Plant("Rose", 25.0, 30)
    print("=== Garden Plant Growth ===")
    rose.show()
    for i in range(1, 8):
        print(f"=== Day {i} ===")
        rose.grow()
        rose.age()
        rose.show()
    print(f"Growth this week: {round(rose.height - 25.0, 1)}cm")


if __name__ == "__main__":
    ft_plant_growth()
