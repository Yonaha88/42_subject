def ft_plant_age() -> None:
    print("Enter plant age in days:", end=' ')
    age = int(input())
    if age <= 60:
        print("Plant needs more time to grow.")
    else:
        print("Plant is ready to harvest!")
