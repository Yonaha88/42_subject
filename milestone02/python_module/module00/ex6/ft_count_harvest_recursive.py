def helper(i: int, n: int) -> None:
    if i > n:
        return
    else:
        print(f"Day {i}")
        helper(i + 1, n)


def ft_count_harvest_recursive() -> None:
    n = int(input("Days until harvest: "))
    helper(1, n)
    print("Harvest time!")
