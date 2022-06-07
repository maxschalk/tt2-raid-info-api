import datetime
import random
from random import randint, choice

from faker import Faker

from src.models.raid_data import *
from src.models.titan_anatomy import *

fake = Faker()
Faker.seed(0)

random.seed(0)


def mock_buff() -> Buff:
    return Buff(
        bonus_type=fake.pystr(),
        bonus_amount=fake.pyfloat()
    )


def mock_titan_anatomy() -> TitanAnatomy:
    return choice(TITAN_PARTS_ATOMIC)


def mock_titan_part() -> TitanPart:
    return TitanPart(
        part_id=mock_titan_anatomy().value,
        total_hp=fake.pyfloat(),
        cursed=fake.pybool()
    )


def mock_enhanced_titan_part() -> EnhancedTitanPart:
    return EnhancedTitanPart(
        part_id=mock_titan_anatomy(),
        total_hp=fake.pyfloat(),
        cursed=fake.pybool(),
        total_hp_formatted=fake.pystr()
    )


def mock_consolidated_titan_part() -> ConsolidateditanPart:
    return ConsolidateditanPart(
        part_id=mock_titan_anatomy(),
        armor_hp=choice((fake.pyfloat(), fake.pyint())),
        body_hp=choice((fake.pyfloat(), fake.pyint())),
        armor_cursed=fake.pybool(),
        body_cursed=fake.pybool()
    )


def mock_titan() -> Titan:
    return Titan(
        enemy_id=fake.pystr(),
        enemy_name=fake.pystr(),
        total_hp=fake.pyfloat(),
        parts=[mock_titan_part() for _ in range(randint(0, 3))],
        area_debuffs=[mock_buff() for _ in range(randint(0, 3))],
        cursed_debuffs=[mock_buff() for _ in range(randint(0, 3))]
    )


def mock_enhanced_titan() -> EnhancedTitan:
    return EnhancedTitan(
        enemy_id=fake.pystr(),
        enemy_name=fake.pystr(),
        total_hp=fake.pyfloat(),
        parts=[mock_titan_part() for _ in range(randint(0, 3))],
        area_debuffs=[mock_buff() for _ in range(randint(0, 3))],
        cursed_debuffs=[mock_buff() for _ in range(randint(0, 3))],
        total_armor_hp=choice((fake.pyfloat(), fake.pyint())),
        total_armor_hp_formatted=fake.pystr(),
        total_body_hp=choice((fake.pyfloat(), fake.pyint())),
        total_body_hp_formatted=fake.pystr(),
        skippable_hp=choice((fake.pyfloat(), fake.pyint())),
        skippable_hp_formatted=fake.pystr(),
        consolidated_parts=[mock_consolidated_titan_part() for _ in range(randint(3, 10))],
        cursed_parts=[mock_enhanced_titan_part() for _ in range(randint(3, 10))],
        number_of_cursed_parts=fake.pyint()
    )


def mock_raid_raw_seed_data() -> RaidRawSeedData:
    titans = [mock_titan() for _ in range(randint(3, 10))]

    valid_from = fake.unique.date_time_between_dates(
        datetime_start="+200y",
        datetime_end="+202y",
    ).replace(
        hour=0,
        minute=0,
        second=1,
    )

    expire_at = valid_from + datetime.timedelta(days=7, seconds=-1)

    return RaidRawSeedData(
        spawn_sequence=[choice(titans).enemy_name for _ in range(randint(3, 10))],
        raid_info_valid_from=valid_from.isoformat(),
        raid_info_expire_at=expire_at.isoformat(),
        tier=str(fake.pyint()),
        level=str(fake.pyint()),
        titans=titans,
        area_buffs=[mock_buff() for _ in range(randint(0, 5))]
    )


def mock_raid_enhanced_seed_data() -> RaidEnhancedSeedData:
    valid_from = fake.unique.date_time_between_dates(
        datetime_start="+200y",
        datetime_end="+202y",
    ).replace(
        hour=0,
        minute=0,
        second=1,
    )

    expire_at = valid_from + datetime.timedelta(days=7, seconds=-1)

    return RaidEnhancedSeedData(
        spawn_sequence=[fake.pystr() for _ in range(randint(3, 10))],
        raid_info_valid_from=valid_from.isoformat(),
        raid_info_expire_at=expire_at.isoformat(),
        tier=str(fake.pyint()),
        level=str(fake.pyint()),
        area_buffs=choice((None, [mock_buff() for _ in range(randint(3, 10))])),
        raid_total_target_hp=choice((fake.pyfloat(), fake.pyint())),
        raid_total_target_hp_formatted=fake.pystr(),
        titans=[mock_enhanced_titan() for _ in range(randint(3, 10))]
    )


def mock_raid_seed_data_filename() -> str:
    fake_date = fake.unique.date_time_between_dates(
        datetime_start="+200y",
        datetime_end="+202y",
    )

    return f"test_raid_seed_{fake_date.strftime('%Y%m%d')}.json"


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
