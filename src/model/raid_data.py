from typing import Any, List, Optional, Union

from fastapi.encoders import jsonable_encoder
# pylint: disable=no-name-in-module
from pydantic import BaseModel, StrictStr, ValidationError
from src.model.seed_type import SeedType


class Buff(BaseModel):
    bonus_type: StrictStr
    bonus_amount: float


class TitanPart(BaseModel):
    part_id: StrictStr
    total_hp: float
    cursed: Optional[bool]

    class Config:
        use_enum_values = True


class Titan(BaseModel):
    enemy_id: StrictStr
    enemy_name: StrictStr

    total_hp: float
    parts: List[TitanPart]

    area_debuffs: List[Buff] = None
    cursed_debuffs: List[Buff] = None


class RaidInfoRaw(BaseModel):
    spawn_sequence: List[StrictStr]

    raid_info_valid_from: str
    raid_info_expire_at: str

    tier: int
    level: int

    titans: List[Titan]

    area_buffs: List[Buff] = None


class EnhancedTitanPart(TitanPart):
    cursed: bool
    total_hp_formatted: StrictStr


class ConsolidatedTitanPart(BaseModel):
    part_id: StrictStr

    armor_hp: Union[int, float]
    body_hp: Union[int, float]

    armor_hp_formatted: StrictStr
    body_hp_formatted: StrictStr

    armor_cursed: bool
    body_cursed: bool

    class Config:
        use_enum_values = True


class EnhancedTitan(Titan):
    parts: List[EnhancedTitanPart]

    total_hp_formatted: StrictStr

    total_armor_hp: Union[int, float]
    total_armor_hp_formatted: StrictStr

    total_body_hp: Union[int, float]
    total_body_hp_formatted: StrictStr

    skippable_hp: Union[int, float]
    skippable_hp_formatted: StrictStr

    consolidated_parts: List[ConsolidatedTitanPart]

    cursed_parts: List[EnhancedTitanPart]
    number_of_cursed_parts: int


class RaidInfoEnhanced(RaidInfoRaw):
    raid_total_target_hp: Union[int, float]
    raid_total_target_hp_formatted: StrictStr

    titans: List[EnhancedTitan]


RaidInfo = Union[RaidInfoRaw, RaidInfoEnhanced]

RaidSeedRaw = List[RaidInfoRaw]
RaidSeedEnhanced = List[RaidInfoEnhanced]

RaidSeed = Union[RaidSeedRaw, RaidInfoEnhanced]


def is_of_seed_type(*, data: Any, seed_type: SeedType) -> bool:
    try:
        data_type = RaidInfoRaw if seed_type == SeedType.RAW else RaidInfoEnhanced

        return all(type(elem) == data_type for elem in data)
    except Exception:
        return False


def map_to_native_object(*, data: Any) -> Any:
    return jsonable_encoder(data)


def map_to_raid_info(*, data: Any, seed_type: Optional[SeedType]) -> RaidInfo:
    if seed_type is None:
        try:
            return RaidInfoEnhanced(**data)
        except ValidationError:
            return RaidInfoRaw(**data)

    else:
        data_type = RaidInfoRaw if seed_type == SeedType.RAW else RaidInfoEnhanced

        return data_type(**data)


def map_to_raid_seed(*, data: Any, seed_type: Optional[SeedType]) -> RaidSeed:
    return list(
        map(lambda item: map_to_raid_info(data=item, seed_type=seed_type),
            data))
