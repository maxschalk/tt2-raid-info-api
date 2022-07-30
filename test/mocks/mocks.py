import datetime
import random
from random import choice, randint
from typing import Iterator

from faker import Faker
from src.model.raid_data import (Buff, ConsolidatedTitanPart, EnhancedTitan,
                                 EnhancedTitanPart, RaidSeedDataEnhanced,
                                 RaidSeedDataRaw, Titan, TitanPart)
from src.model.titan_anatomy import TITAN_PARTS_ATOMIC, TitanAnatomy

fake = Faker()
Faker.seed(0)

random.seed(0)


def mock_buff() -> Buff:
    return Buff(bonus_type=fake.pystr(), bonus_amount=fake.pyfloat())


def mock_titan_anatomy() -> TitanAnatomy:
    return choice(TITAN_PARTS_ATOMIC)


def mock_titan_part() -> TitanPart:
    return TitanPart(part_id=mock_titan_anatomy().value,
                     total_hp=fake.pyfloat(),
                     cursed=fake.pybool())


def mock_enhanced_titan_part() -> EnhancedTitanPart:
    return EnhancedTitanPart(part_id=mock_titan_anatomy().value,
                             total_hp=fake.pyfloat(),
                             cursed=fake.pybool(),
                             total_hp_formatted=fake.pystr())


def mock_consolidated_titan_part() -> ConsolidatedTitanPart:
    armor_hp = choice((fake.pyfloat(), fake.pyint()))

    body_hp = choice((fake.pyfloat(), fake.pyint()))

    return ConsolidatedTitanPart(part_id=mock_titan_anatomy().value,
                                 armor_hp=armor_hp,
                                 armor_hp_formatted=str(armor_hp),
                                 body_hp=body_hp,
                                 body_hp_formatted=str(body_hp),
                                 armor_cursed=fake.pybool(),
                                 body_cursed=fake.pybool())


def mock_titan() -> Titan:
    return Titan(enemy_id=fake.pystr(),
                 enemy_name=fake.pystr(),
                 total_hp=fake.pyfloat(),
                 parts=[mock_titan_part() for _ in range(randint(0, 3))],
                 area_debuffs=[mock_buff() for _ in range(randint(0, 3))],
                 cursed_debuffs=[mock_buff() for _ in range(randint(0, 3))])


def mock_enhanced_titan() -> EnhancedTitan:
    total_hp = fake.pyfloat()
    total_armor_hp = choice((fake.pyfloat(), fake.pyint()))
    total_body_hp = choice((fake.pyfloat(), fake.pyint()))
    skippable_hp = choice((fake.pyfloat(), fake.pyint()))

    return EnhancedTitan(
        enemy_id=fake.pystr(),
        enemy_name=fake.pystr(),
        total_hp=total_hp,
        total_hp_formatted=str(total_hp),
        parts=[mock_enhanced_titan_part() for _ in range(randint(0, 3))],
        area_debuffs=[mock_buff() for _ in range(randint(0, 3))],
        cursed_debuffs=[mock_buff() for _ in range(randint(0, 3))],
        total_armor_hp=total_armor_hp,
        total_armor_hp_formatted=str(total_armor_hp),
        total_body_hp=total_body_hp,
        total_body_hp_formatted=str(total_body_hp),
        skippable_hp=skippable_hp,
        skippable_hp_formatted=str(skippable_hp),
        consolidated_parts=[
            mock_consolidated_titan_part() for _ in range(randint(3, 10))
        ],
        cursed_parts=[
            mock_enhanced_titan_part() for _ in range(randint(3, 10))
        ],
        number_of_cursed_parts=fake.pyint())


def _mock_raid_raw_seed_data_gen() -> Iterator[RaidSeedDataRaw]:
    valid_from = datetime.datetime(1970, 1, 1, 0, 0, 1)

    while True:
        valid_from = valid_from + datetime.timedelta(days=-7)

        expire_at = valid_from + datetime.timedelta(days=7, seconds=-1)

        titans = [mock_titan() for _ in range(randint(3, 10))]

        yield RaidSeedDataRaw(
            spawn_sequence=[
                choice(titans).enemy_name for _ in range(randint(3, 10))
            ],
            raid_info_valid_from=valid_from.isoformat(),
            raid_info_expire_at=expire_at.isoformat(),
            tier=str(fake.unique.pyint()),
            level=str(fake.unique.pyint()),
            titans=titans,
            area_buffs=[mock_buff() for _ in range(randint(3, 10))])


MOCK_RAID_RAW_SEED_DATA_GEN = _mock_raid_raw_seed_data_gen()


def mock_raid_raw_seed_data() -> RaidSeedDataRaw:
    return next(MOCK_RAID_RAW_SEED_DATA_GEN)


def _mock_raid_enhanced_seed_data_gen() -> Iterator[RaidSeedDataEnhanced]:
    valid_from = datetime.datetime(1970, 1, 1, 0, 0, 1)

    while True:
        valid_from = valid_from + datetime.timedelta(days=-7)

        expire_at = valid_from + datetime.timedelta(days=7, seconds=-1)

        yield RaidSeedDataEnhanced(
            spawn_sequence=[fake.pystr() for _ in range(randint(3, 10))],
            raid_info_valid_from=valid_from.isoformat(),
            raid_info_expire_at=expire_at.isoformat(),
            tier=str(fake.unique.pyint()),
            level=str(fake.unique.pyint()),
            area_buffs=[mock_buff() for _ in range(randint(3, 10))],
            raid_total_target_hp=choice((fake.pyfloat(), fake.pyint())),
            raid_total_target_hp_formatted=fake.pystr(),
            titans=[mock_enhanced_titan() for _ in range(randint(3, 10))])


MOCK_RAID_ENHANCED_SEED_DATA_GEN = _mock_raid_enhanced_seed_data_gen()


def mock_raid_enhanced_seed_data() -> RaidSeedDataEnhanced:
    return next(MOCK_RAID_ENHANCED_SEED_DATA_GEN)


def _mock_raid_seed_data_filename_gen() -> Iterator[str]:
    valid_from = datetime.datetime(1970, 1, 1, 0, 0, 1)

    while True:
        valid_from = valid_from + datetime.timedelta(days=-7)

        yield f"raid_seed_{valid_from.strftime('%Y%m%d')}_test.json"


MOCK_RAID_SEED_DATA_FILENAME_GEN = _mock_raid_seed_data_filename_gen()


def mock_raid_seed_data_filename() -> str:
    return next(MOCK_RAID_SEED_DATA_FILENAME_GEN)


if __name__ == '__main__':
    print("mock_buff:", mock_buff())
    print("mock_titan_anatomy:", mock_titan_anatomy())
    print("mock_titan_part:", mock_titan_part())
    print("mock_enhanced_titan_part:", mock_enhanced_titan_part())
    print("mock_consolidated_titan_part:", mock_consolidated_titan_part())
    print("mock_titan:", mock_titan())
    print("mock_enhanced_titan:", mock_enhanced_titan())
    print("mock_raid_raw_seed_data:", mock_raid_raw_seed_data())
    print("mock_raid_enhanced_seed_data:", mock_raid_enhanced_seed_data())
    print("mock_raid_seed_data_filename:", mock_raid_seed_data_filename())
