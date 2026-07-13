#!/usr/bin/env python3


def artifact_sorter(artifacts: list[dict]) -> list[dict]:
    return sorted(artifacts, key=lambda a: a["power"], reverse=True)


def power_filter(mages: list[dict], min_power: int) -> list[dict]:
    return list(filter(lambda m: m["power"] >= min_power, mages))


def spell_transformer(spells: list[str]) -> list[str]:
    return list(map(lambda s: f"* {s} *", spells))


def mage_stats(mages: list[dict]) -> dict:
    powers = list(map(lambda m: m["power"], mages))
    return {
        "max_power": max(powers),
        "min_power": min(powers),
        "avg_power": round(sum(powers) / len(powers), 2),
    }


def main() -> None:
    artifacts = [
        {"name": "Crystal Orb", "power": 85, "type": "orb"},
        {"name": "Fire Staff", "power": 92, "type": "staff"},
        {"name": "Ice Wand", "power": 70, "type": "wand"},
    ]
    mages = [
        {"name": "Alex", "power": 95, "element": "fire"},
        {"name": "Jordan", "power": 60, "element": "water"},
        {"name": "Riley", "power": 80, "element": "earth"},
    ]

    print("Testing artifact sorter...")
    ordered = artifact_sorter(artifacts)
    top, second = ordered[0], ordered[1]
    print(
        f"{top['name']} ({top['power']} power) comes before "
        f"{second['name']} ({second['power']} power)"
    )
    print()

    print("Testing power filter...")
    strong = power_filter(mages, 75)
    print(", ".join(map(lambda m: m["name"], strong)))
    print()

    print("Testing spell transformer...")
    print(" ".join(spell_transformer(["fireball", "heal", "shield"])))
    print()

    print("Testing mage stats...")
    print(mage_stats(mages))


if __name__ == "__main__":
    main()
