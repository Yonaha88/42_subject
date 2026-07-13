#!/usr/bin/env python3

class Plant:
    class _Stats:
        def __init__(self) -> None:
            self._grow_count = 0
            self._age_count = 0
            self._show_count = 0

        def show(self) -> None:
            print(
                f"Stats: {self._grow_count} grow, "
                f"{self._age_count} age, "
                f"{self._show_count} show"
            )

    def __init__(self, name: str, height: float, days: int) -> None:
        self.name = name
        self._height = 0.0
        self._age = 0
        self._stats = Plant._Stats()
        self.set_height(height)
        self.set_age(days)

    def show(self) -> None:
        self._stats._show_count += 1
        print(f"{self.name}: {round(self._height, 1)}cm, {self._age} days old")

    def grow(self) -> None:
        self._stats._grow_count += 1
        self._height += 8.0

    def age(self) -> None:
        self._stats._age_count += 1
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

    @staticmethod
    def is_older_than_one_year(age: int) -> bool:
        return age > 365

    @classmethod
    def anonymous(cls) -> 'Plant':
        return cls("Unknown plant", 0.0, 0)


class Flower(Plant):
    def __init__(
        self, name: str, height: float, days: int, color: str
    ) -> None:
        super().__init__(name, height, days)
        self.color = color
        self._bloomed = False

    def show(self) -> None:
        super().show()
        print(f" Color: {self.color}")
        if self._bloomed:
            print(f" {self.name} is blooming beautifully!")
        else:
            print(f" {self.name} has not bloomed yet")

    def bloom(self) -> None:
        self._bloomed = True


class Tree(Plant):
    class _Stats(Plant._Stats):
        def __init__(self) -> None:
            super().__init__()
            self._shade_count = 0

        def show(self) -> None:
            super().show()
            print(f" {self._shade_count} shade")

    def __init__(
        self, name: str, height: float, days: int, trunk_diameter: float
    ) -> None:
        super().__init__(name, height, days)
        self.trunk_diameter = trunk_diameter
        self._stats: Tree._Stats = Tree._Stats()

    def show(self) -> None:
        super().show()
        print(f" Trunk diameter: {round(self.trunk_diameter, 1)}cm")

    def produce_shade(self) -> None:
        self._stats._shade_count += 1
        print(
            f"Tree {self.name} now produces a shade of "
            f"{round(self._height, 1)}cm long and "
            f"{round(self.trunk_diameter, 1)}cm wide."
        )


class Vegetable(Plant):
    def __init__(
        self, name: str, height: float, days: int, harvest_season: str
    ) -> None:
        super().__init__(name, height, days)
        self.harvest_season = harvest_season
        self.nutritional_value = 0

    def show(self) -> None:
        super().show()
        print(f" Harvest season: {self.harvest_season}")
        print(f" Nutritional value: {self.nutritional_value}")

    def grow(self) -> None:
        self._stats._grow_count += 1
        self._height += 2.1

    def age(self) -> None:
        self._stats._age_count += 1
        self._age += 1
        self.nutritional_value += 1


class Seed(Flower):
    def __init__(
        self, name: str, height: float, days: int, color: str,
        seed_count: int = 0,
    ) -> None:
        super().__init__(name, height, days, color)
        self.seed_count = seed_count

    def show(self) -> None:
        super().show()
        print(f" Seeds: {self.seed_count}")

    def grow(self) -> None:
        self._stats._grow_count += 1
        self._height += 30.0

    def age(self) -> None:
        self._stats._age_count += 1
        self._age += 20

    def bloom(self) -> None:
        super().bloom()
        self.seed_count += 1


def display_stats(plant: Plant) -> None:
    print(f"[statistics for {plant.name}]")
    plant._stats.show()


def ft_garden_analytics() -> None:
    print("=== Garden statistics ===")
    print("=== Check year-old")
    older = Plant.is_older_than_one_year
    print(f"Is 30 days more than a year? -> {older(30)}")
    print(f"Is 400 days more than a year? -> {older(400)}")
    print()

    print("=== Flower")
    rose = Flower("Rose", 15.0, 10, "red")
    rose.show()
    display_stats(rose)
    print("[asking the rose to grow and bloom]")
    rose.grow()
    rose.bloom()
    rose.show()
    display_stats(rose)
    print()

    print("=== Tree")
    oak = Tree("Oak", 200.0, 365, 5.0)
    oak.show()
    display_stats(oak)
    print("[asking the oak to produce shade]")
    oak.produce_shade()
    display_stats(oak)
    print()

    print("=== Seed")
    sunflower = Seed("Sunflower", 80.0, 45, "yellow")
    sunflower.show()
    print("[make sunflower grow, age and bloom]")
    sunflower.grow()
    sunflower.age()
    for _ in range(42):
        sunflower.bloom()
    sunflower.show()
    display_stats(sunflower)
    print()

    print("=== Anonymous")
    anon = Plant.anonymous()
    anon.show()
    display_stats(anon)


if __name__ == "__main__":
    ft_garden_analytics()
