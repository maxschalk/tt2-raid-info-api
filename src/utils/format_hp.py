def format_hp(hp: int | float):
    thousands_units = ["K", "M", "B", "T", "Q"]
    unit = ""

    hp = int(hp)

    while hp >= 1000 and len(thousands_units):
        hp = int(((hp / 1000) * 100)) / 100

        unit = thousands_units.pop(0)

    return f"{hp:.2f}{unit}"
