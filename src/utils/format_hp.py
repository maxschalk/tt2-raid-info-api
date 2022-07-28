from typing import Union


def format_healthpoints(healthpoints: Union[int, float]):
    thousands_units = ["K", "M", "B", "T", "Q"]
    unit = ""

    healthpoints = int(healthpoints)

    while healthpoints >= 1000 and thousands_units:
        healthpoints = int(((healthpoints / 1000) * 100)) / 100

        unit = thousands_units.pop(0)

    return f"{healthpoints:.2f}{unit}"
