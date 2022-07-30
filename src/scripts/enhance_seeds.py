import os
from typing import List

from src.domain.filesystem_seed_data_repository import \
    FSSeedDataRepository
from src.model.raid_data import (ConsolidatedTitanPart, EnhancedTitan,
                                 EnhancedTitanPart, RaidSeedDataRaw, Titan,
                                 TitanPart)
from src.model.seed_type import SeedType
from src.model.titan_anatomy import (ARMOR_PREFIX, BODY_PREFIX,
                                     TITAN_PARTS_ATOMIC)
from src.paths import DATA_DIR, ENHANCED_SEEDS_DIR, RAW_SEEDS_DIR
from src.utils import selectors
from src.utils.format_hp import format_healthpoints
from src.utils.temp_deepcopy import temp_deepcopy

seed_data_repo = FSSeedDataRepository(base_path=DATA_DIR)


def main():
    raw_seed_paths = set(
        seed_data_repo.list_seed_identifiers(seed_type=SeedType.RAW))
    enhanced_seed_paths = set(
        seed_data_repo.list_seed_identifiers(seed_type=SeedType.ENHANCED))

    delete_seed_ids = enhanced_seed_paths - raw_seed_paths

    enhance_seed_ids = raw_seed_paths - enhanced_seed_paths

    for seed_id in delete_seed_ids:
        seed_data_repo.delete_seed(identifier=seed_id,
                                   seed_type=SeedType.ENHANCED)

    for seed_id in enhance_seed_ids:
        raw_seed_data = seed_data_repo.get_seed_by_identifier(
            identifier=seed_id, seed_type=SeedType.RAW)

        enhanced_seed_data = list(
            map(enhance_raid_info, temp_deepcopy(raw_seed_data)))

        success = seed_data_repo.save_seed(identifier=seed_id,
                                           seed_type=SeedType.ENHANCED,
                                           data=enhanced_seed_data)

        if not success:
            print(f"Could not enhance {seed_id}")


def enhance_raid_info(raid_info: RaidSeedDataRaw) -> RaidSeedDataRaw:
    raid_total_target_hp = selectors.raid_target_hp(raid_info)
    raid_info['raid_total_target_hp'] = raid_total_target_hp
    raid_info['raid_total_target_hp_formatted'] = format_healthpoints(
        raid_total_target_hp)

    raid_info_titans = selectors.raid_titans(raid_info)

    enhanced_titans = list(map(enhance_titan_info, raid_info_titans))

    raid_info['titans'] = enhanced_titans

    return raid_info


def enhance_titan_info(titan_info: Titan) -> EnhancedTitan:
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
    enhanced_parts = list(map(enhance_titan_part, titan_info_parts))
    titan_info['parts'] = enhanced_parts

    consolidated_parts = consolidated_titan_parts(titan_info)
    titan_info['consolidated_parts'] = consolidated_parts

    cursed_parts = selectors.titan_cursed_parts(titan_info)
    titan_info['cursed_parts'] = cursed_parts
    titan_info['number_of_cursed_parts'] = len(cursed_parts)

    return titan_info


def enhance_titan_part(titan_part_info: TitanPart) -> EnhancedTitanPart:
    titan_part_total_hp = selectors.titan_part_hp(titan_part_info)
    titan_part_info['total_hp_formatted'] = format_healthpoints(
        titan_part_total_hp)

    cursed = selectors.titan_part_cursed(titan_part_info)
    titan_part_info['cursed'] = False if cursed is None else cursed

    return titan_part_info


def consolidated_titan_parts(titan_info: Titan) -> List[ConsolidatedTitanPart]:
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


if __name__ == '__main__':
    main()
