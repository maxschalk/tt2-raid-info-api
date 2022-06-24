import os
from src.models.raid_data import ConsolidatedTitanPart, EnhancedTitan, EnhancedTitanPart, RaidSeedDataRaw, Titan, TitanPart

from src.models.titan_anatomy import (ARMOR_PREFIX, BODY_PREFIX,
                                      TITAN_PARTS_ATOMIC)
from src.PATHS import ENHANCED_SEEDS_DIR, RAW_SEEDS_DIR
from src.utils import selectors
from src.utils.format_hp import format_hp
from src.utils.seed_data_fs_interface import (dump_seed_data,
                                              get_all_seed_filenames,
                                              load_seed_data)
from src.utils.temp_deepcopy import temp_deepcopy


def main():
    raw_seed_paths = set(get_all_seed_filenames(dir_path=RAW_SEEDS_DIR))
    enhanced_seed_paths = set(
        get_all_seed_filenames(dir_path=ENHANCED_SEEDS_DIR))

    delete_seed_filenames = enhanced_seed_paths - raw_seed_paths

    enhance_seed_filenames = raw_seed_paths - enhanced_seed_paths

    for filename in delete_seed_filenames:
        filepath = os.path.join(ENHANCED_SEEDS_DIR, filename)

        os.remove(filepath)

    for filename in enhance_seed_filenames:
        filepath_raw_seed = os.path.join(RAW_SEEDS_DIR, filename)
        raw_seed_data = load_seed_data(filepath=filepath_raw_seed)

        enhanced_seed_data = list(
            map(enhance_raid_info, temp_deepcopy(raw_seed_data))
        )

        filepath_enhanced_seed = os.path.join(ENHANCED_SEEDS_DIR, filename)

        dump_seed_data(
            filepath=filepath_enhanced_seed,
            data=enhanced_seed_data
        )


def enhance_raid_info(raid_info: RaidSeedDataRaw) -> RaidSeedDataRaw:
    raid_total_target_hp = selectors.raid_target_hp(raid_info)
    raid_info['raid_total_target_hp'] = raid_total_target_hp
    raid_info['raid_total_target_hp_formatted'] = format_hp(
        raid_total_target_hp)

    raid_info_titans = selectors.raid_titans(raid_info)

    enhanced_titans = list(map(enhance_titan_info, raid_info_titans))

    raid_info['titans'] = enhanced_titans

    return raid_info


def enhance_titan_info(titan_info: Titan) -> EnhancedTitan:
    titan_total_hp = selectors.titan_total_hp(titan_info)
    titan_info['total_hp_formatted'] = format_hp(titan_total_hp)

    titan_total_armor_hp = selectors.titan_total_armor_hp(titan_info)
    titan_info['total_armor_hp'] = titan_total_armor_hp
    titan_info['total_armor_hp_formatted'] = format_hp(titan_total_armor_hp)

    titan_total_body_hp = selectors.titan_total_body_hp(titan_info)
    titan_info['total_body_hp'] = titan_total_body_hp
    titan_info['total_body_hp_formatted'] = format_hp(titan_total_body_hp)

    titan_skippable_hp = selectors.titan_skippable_hp(titan_info)
    titan_info['skippable_hp'] = titan_skippable_hp
    titan_info['skippable_hp_formatted'] = format_hp(titan_skippable_hp)

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
    titan_part_info['total_hp_formatted'] = format_hp(titan_part_total_hp)

    cursed = selectors.titan_part_cursed(titan_part_info)
    titan_part_info['cursed'] = False if cursed is None else cursed

    return titan_part_info


def consolidated_titan_parts(titan_info: Titan) -> list[ConsolidatedTitanPart]:
    titan_parts = selectors.titan_parts(titan_info)

    consolidated_parts = []

    for part in TITAN_PARTS_ATOMIC:
        part_id = part.value

        consolidated_part = {
            "part_id": part_id,

            "armor_hp": 0,
            "armor_hp_formatted": 0,

            "body_hp": 0,
            "body_hp_formatted": 0,

            "armor_cursed": False,
            "body_cursed": False,
        }

        for titan_part in titan_parts:
            titan_part_part_id = titan_part['part_id']

            if titan_part_part_id.endswith(part_id):

                if titan_part_part_id.startswith(ARMOR_PREFIX):
                    consolidated_part['armor_hp'] = titan_part['total_hp']
                    consolidated_part['armor_hp_formatted'] = format_hp(
                        titan_part['total_hp'])

                    if 'cursed' in titan_part:
                        consolidated_part['armor_cursed'] = titan_part['cursed']

                elif titan_part_part_id.startswith(BODY_PREFIX):
                    consolidated_part['body_hp'] = titan_part['total_hp']
                    consolidated_part['body_hp_formatted'] = format_hp(
                        titan_part['total_hp'])

                    if 'cursed' in titan_part:
                        consolidated_part['body_cursed'] = titan_part['cursed']

        consolidated_parts.append(consolidated_part)

    return consolidated_parts


if __name__ == '__main__':
    main()
