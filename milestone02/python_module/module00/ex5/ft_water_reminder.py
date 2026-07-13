def ft_water_reminder() -> None:
    print("Days since last watering:", end=' ')
    last_water = int(input())
    if last_water < 3:
        print("Plants are fine")
    else:
        print("Water the plants!")
