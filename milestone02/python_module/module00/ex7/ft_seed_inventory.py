def ft_seed_inventory(seed_type: str, quantity: int, unit: str) -> None:
    if unit == "packets":
        print(f"{seed_type.capitalize()} seeds: ", end='')
        print(f"{quantity} packets available")
    elif unit == "grams":
        print(f"{seed_type.capitalize()} seeds: ", end='')
        print(f"{quantity} grams total")
    elif unit == "area":
        print(f"{seed_type.capitalize()} seeds: ", end='')
        print(f"covers {quantity} square meters")
    else:
        print("Unknown unit type")
