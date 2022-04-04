def format_hp(hp: int | float):
    thousands_units = ["K", "M", "B", "T", "Q"]
    unit = ""

    while hp >= 1000:
        hp /= 1000
        unit = thousands_units.pop(0)

    return f"{hp:.2f}{unit}"
