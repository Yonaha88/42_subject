#!/usr/bin/env python3

def ft_garden_intro(name: str, height: int, age: int) -> None:
    print("=== Welcome to My Garden ===")
    print("Plant:", name)
    print("Height: ", height, "cm", sep='')
    print("Age:", age, "days")
    print("\n=== End of Program ===")


if __name__ == "__main__":
    ft_garden_intro("Rose", 25, 30)
