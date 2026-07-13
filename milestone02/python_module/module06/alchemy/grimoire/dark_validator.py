from .dark_spellbook import dark_spell_allowed_ingredients


def validate_dark_ingredients(ingredients: str) -> str:
    lowered = ingredients.lower()
    for ingredient in dark_spell_allowed_ingredients():
        if ingredient in lowered:
            return f"{ingredients} - VALID"
    return f"{ingredients} - INVALID"
