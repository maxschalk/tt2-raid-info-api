from typing import List

from fastapi.encoders import jsonable_encoder
from src.model.raid_data import (ConsolidatedTitanPart, EnhancedTitan,
                                 EnhancedTitanPart, RaidSeedDataEnhanced,
                                 RaidSeedDataRaw, Titan, TitanPart)
from src.model.titan_anatomy import (ARMOR_PREFIX, BODY_PREFIX,
                                     TITAN_PARTS_ATOMIC)
from src.utils import selectors
from src.utils.format_hp import format_healthpoints


def enhance_seed_data(
        *, data: List[RaidSeedDataRaw]) -> List[RaidSeedDataEnhanced]:

    jsonable = map(jsonable_encoder, data)

    enhanced = map(_enhance_raid_info, jsonable)

    objects = map(lambda elem: RaidSeedDataEnhanced(**elem), enhanced)

    return list(objects)


def _enhance_raid_info(raid_info: RaidSeedDataRaw) -> RaidSeedDataEnhanced:
    raid_total_target_hp = selectors.raid_target_hp(raid_info)
    raid_info['raid_total_target_hp'] = raid_total_target_hp
    raid_info['raid_total_target_hp_formatted'] = format_healthpoints(
        raid_total_target_hp)

    raid_info_titans = selectors.raid_titans(raid_info)

    enhanced_titans = list(map(_enhance_titan_info, raid_info_titans))

    raid_info['titans'] = enhanced_titans

    return raid_info


def _enhance_titan_info(titan_info: Titan) -> EnhancedTitan:
    titan_total_hp = selectors.titan_total_hp(titan_info)
    titan_info['total_hp_formatted'] = format_healthpoints(titan_total_hp)

    titan_total_armor_hp = selectors.titan_total_armor_hp(titan_info)
    titan_info['total_armor_hp'] = titan_total_armor_hp
    titan_info['total_armor_hp_formatted'] = format_healthpoints(
        titan_total_armor_hp)

    titan_total_body_hp = selectors.titan_total_body_hp(titan_info)
    titan_info['total_body_hp'] = titan_total_body_hp
    titan_info['total_body_hp_formatted'] = format_healthpoints(
        titan_total_body_hp)

    titan_skippable_hp = selectors.titan_skippable_hp(titan_info)
    titan_info['skippable_hp'] = titan_skippable_hp
    titan_info['skippable_hp_formatted'] = format_healthpoints(
        titan_skippable_hp)

    titan_info_parts = selectors.titan_parts(titan_info)
    enhanced_parts = list(map(_enhance_titan_part, titan_info_parts))
    titan_info['parts'] = enhanced_parts

    consolidated_parts = _consolidated_titan_parts(titan_info)
    titan_info['consolidated_parts'] = consolidated_parts

    cursed_parts = selectors.titan_cursed_parts(titan_info)
    titan_info['cursed_parts'] = cursed_parts
    titan_info['number_of_cursed_parts'] = len(cursed_parts)

    return titan_info


def _enhance_titan_part(titan_part_info: TitanPart) -> EnhancedTitanPart:
    titan_part_total_hp = selectors.titan_part_hp(titan_part_info)
    titan_part_info['total_hp_formatted'] = format_healthpoints(
        titan_part_total_hp)

    cursed = selectors.titan_part_cursed(titan_part_info)
    titan_part_info['cursed'] = False if cursed is None else cursed

    return titan_part_info


def _consolidated_titan_parts(
        titan_info: Titan) -> List[ConsolidatedTitanPart]:
    titan_parts = selectors.titan_parts(titan_info)

    consolidated_parts = []

    for part in TITAN_PARTS_ATOMIC:
        part_id = part.value

        consolidated_part = {
            "part_id": part_id,
            "armor_hp": 0,
            "armor_hp_formatted": "0",
            "body_hp": 0,
            "body_hp_formatted": "0",
            "armor_cursed": False,
            "body_cursed": False,
        }

        for titan_part in titan_parts:
            titan_part_part_id = titan_part['part_id']

            if titan_part_part_id.endswith(part_id):

                if titan_part_part_id.startswith(ARMOR_PREFIX):
                    consolidated_part['armor_hp'] = titan_part['total_hp']
                    consolidated_part[
                        'armor_hp_formatted'] = format_healthpoints(
                            titan_part['total_hp'])

                    if 'cursed' in titan_part:
                        consolidated_part['armor_cursed'] = titan_part[
                            'cursed']

                elif titan_part_part_id.startswith(BODY_PREFIX):
                    consolidated_part['body_hp'] = titan_part['total_hp']
                    consolidated_part[
                        'body_hp_formatted'] = format_healthpoints(
                            titan_part['total_hp'])

                    if 'cursed' in titan_part:
                        consolidated_part['body_cursed'] = titan_part['cursed']

        consolidated_parts.append(consolidated_part)

    return consolidated_parts
