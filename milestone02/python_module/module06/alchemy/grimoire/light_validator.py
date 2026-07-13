def validate_ingredients(ingredients: str) -> str:
    from .light_spellbook import light_spell_allowed_ingredients

    lowered = ingredients.lower()
    for ingredient in light_spell_allowed_ingredients():
        if ingredient in lowered:
            return f"{ingredients} - VALID"
    return f"{ingredients} - INVALID"
