from datetime import datetime
from functools import reduce
from typing import Dict, List, Optional, Tuple

import src.models.titan_anatomy as titan_anatomy
from src.models.ValidatorBinOp import ValidatorBinOp
from src.utils.safe_parse import (safe_parse_datetime, safe_parse_float,
                                  safe_parse_int)

# top level utility functions


def select_first_by(data,
                    selectors_and_validators,
                    bin_op: ValidatorBinOp = ValidatorBinOp.AND):
    validator = reduce(
        lambda acc, elem: (lambda x: bin_op.func(acc(x), elem[1](elem[0](x)))),
        selectors_and_validators, lambda x: bin_op.initial)

    try:
        return next(filter(validator, data))
    except StopIteration:
        return None


def select_all_by(data,
                  selectors_and_validators,
                  bin_op: ValidatorBinOp = ValidatorBinOp.AND):
    validator = reduce(
        lambda acc, elem: (lambda x: bin_op.func(acc(x), elem[1](elem[0](x)))),
        selectors_and_validators, lambda x: bin_op.initial)

    return tuple(filter(validator, data))


# trivial top level selectors


def raid_spawn_sequence(raid_info: dict) -> List[str]:
    return raid_info.get("spawn_sequence", [])


def raid_valid_from(raid_info: dict) -> Optional[datetime]:
    return safe_parse_datetime(raid_info.get("raid_info_valid_from"))


def raid_valid_until(raid_info: dict) -> Optional[datetime]:
    return safe_parse_datetime(raid_info.get("raid_info_expire_at"))


def raid_tier(raid_info: dict) -> Optional[int]:
    return safe_parse_int(raid_info.get("tier"))


def raid_level(raid_info: dict) -> Optional[int]:
    return safe_parse_int(raid_info.get("level"))


def raid_titans(raid_info: dict) -> List[Dict]:
    return raid_info.get("titans", [])


def raid_area_buffs(raid_info: dict) -> List[Dict]:
    return raid_info.get("area_buffs", [])


# custom top level selectors


def raid_target_hp(raid_info: dict) -> Optional[float]:
    if not (spawn_sequence := raid_spawn_sequence(raid_info)):
        return None

    if not (titans := raid_titans(raid_info)):
        return None

    titans = {titan_name(titan): titan for titan in titans}

    titan_spawns = (titans[name] for name in spawn_sequence)

    return sum(map(titan_total_hp, titan_spawns))


# buff / debuff selectors


def buff_bonus_type(buff_info) -> Optional[str]:
    return buff_info.get("bonus_type")


def buff_bonus_amount(buff_info) -> Optional[float]:
    return safe_parse_float(buff_info.get("bonus_amount"))


# titan selectors


def titan_name(titan_info) -> Optional[str]:
    return titan_info.get("enemy_name")


def titan_total_hp(titan_info) -> Optional[float]:
    return titan_info.get("total_hp")


def titan_parts(titan_info) -> List[Dict]:
    return titan_info.get("parts", [])


def titan_area_debuffs(titan_info) -> List[Dict]:
    return titan_info.get("area_debuffs", [])


def titan_cursed_debuffs(titan_info) -> List[Dict]:
    return titan_info.get("cursed_debuffs", [])


# custom titan selectors


def titan_cursed_parts(titan_info) -> Tuple[Dict]:
    return tuple(
        filter(lambda part: titan_part_cursed(part), titan_parts(titan_info)))


def titan_part_by_name(titan_info, part_id) -> Optional[Dict]:
    for part_info in titan_parts(titan_info):
        if titan_part_name(part_info) == part_id:
            return part_info

    return None


def titan_subparts_by_object(
        titan_info,
        part_object,
        prefix=titan_anatomy.BODY_PREFIX) -> Tuple[Optional[Dict]]:
    if part_object not in titan_anatomy.TITAN_PARTS_ALL:
        raise ValueError("Incorrect part object provided")

    if isinstance(part_object, str):
        return titan_part_by_name(titan_info, f"{prefix}{part_object}"),

    return tuple(
        map(lambda part: titan_part_by_name(titan_info, f"{prefix}{part}"),
            part_object))


def titan_total_armor_hp(titan_info) -> Optional[float]:
    return _sum_parts_hp_with_prefix(titan_info, titan_anatomy.ARMOR_PREFIX)


def titan_total_body_hp(titan_info) -> Optional[float]:
    return _sum_parts_hp_with_prefix(titan_info, titan_anatomy.BODY_PREFIX)


def titan_skippable_hp(titan_info) -> Optional[float]:
    return titan_total_body_hp(titan_info) - titan_total_hp(titan_info)


def _sum_parts_hp_with_prefix(titan_info, prefix) -> Optional[float]:
    parts = titan_parts(titan_info)
    return sum(
        map(
            titan_part_hp,
            filter(lambda part: titan_part_name(part).startswith(prefix),
                   parts)))


# titan part selectors


def titan_part_name(part_info) -> Optional[str]:
    return part_info.get("part_id")


def titan_part_hp(part_info) -> Optional[float]:
    return part_info.get("total_hp")


def titan_part_cursed(part_info) -> bool:
    return part_info.get("cursed", False)
