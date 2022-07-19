from typing import List, Optional, Union

from pydantic import BaseModel, StrictStr


class RaidDataFile(BaseModel):
    filename: StrictStr


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


class RaidSeedDataRaw(BaseModel):
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


class RaidSeedDataEnhanced(RaidSeedDataRaw):
    raid_total_target_hp: Union[int, float]
    raid_total_target_hp_formatted: StrictStr

    titans: List[EnhancedTitan]


RaidSeedData = Union[RaidSeedDataRaw, RaidSeedDataEnhanced]

# SAMPLE
"""
{
     "spawn_sequence": [
         "Terro",
         "Sterl",
         "Sterl",
         "Takedar",
         "Terro"
     ],
     "raid_info_valid_from": "2022-04-03T00:00:01",
     "raid_info_expire_at": "2022-04-10T00:00:00",
     "tier": "4",
     "level": "49",
     "titans": [
         {
             "enemy_id": "Enemy2",
             "total_hp": 12400000000.0,
             "parts": [
                 {
                     "part_id": "BodyHead",
                     "total_hp": 4464000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHead",
                     "total_hp": 3720000000.0,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyChestUpper",
                     "total_hp": 3720000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorChestUpper",
                     "total_hp": 3100000000.0,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyArmUpperRight",
                     "total_hp": 1162500000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorArmUpperRight",
                     "total_hp": 930000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyArmUpperLeft",
                     "total_hp": 1162500000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorArmUpperLeft",
                     "total_hp": 930000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyLegUpperRight",
                     "total_hp": 1395000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorLegUpperRight",
                     "total_hp": 1395000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyLegUpperLeft",
                     "total_hp": 1395000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorLegUpperLeft",
                     "total_hp": 1395000000.0,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyHandRight",
                     "total_hp": 1162500000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHandRight",
                     "total_hp": 930000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyHandLeft",
                     "total_hp": 1162500000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHandLeft",
                     "total_hp": 930000000.0,
                     "cursed": True
                 }
             ],
             "enemy_name": "Takedar",
             "area_debuffs": [
                 {
                     "bonus_type": "AllLimbsHPMult",
                     "bonus_amount": 0.5
                 }
             ],
             "cursed_debuffs": [
                 {
                     "bonus_type": "AfflictedDamagePerCurse",
                     "bonus_amount": -0.06
                 }
             ]
         },
         {
             "enemy_id": "Enemy4",
             "total_hp": 12400000000.0,
             "parts": [
                 {
                     "part_id": "BodyHead",
                     "total_hp": 2480000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHead",
                     "total_hp": 2480000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyChestUpper",
                     "total_hp": 5728800000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorChestUpper",
                     "total_hp": 2170000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyArmUpperRight",
                     "total_hp": 620000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorArmUpperRight",
                     "total_hp": 775000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyArmUpperLeft",
                     "total_hp": 620000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorArmUpperLeft",
                     "total_hp": 775000000.0,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyLegUpperRight",
                     "total_hp": 1240000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorLegUpperRight",
                     "total_hp": 1550000000.0,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyLegUpperLeft",
                     "total_hp": 1240000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorLegUpperLeft",
                     "total_hp": 1550000000.0,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyHandRight",
                     "total_hp": 620000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHandRight",
                     "total_hp": 775000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyHandLeft",
                     "total_hp": 620000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHandLeft",
                     "total_hp": 775000000.0,
                     "cursed": True
                 }
             ],
             "enemy_name": "Sterl",
             "area_debuffs": [
                 {
                     "bonus_type": "AllTorsoHPMult",
                     "bonus_amount": -0.3
                 }
             ],
             "cursed_debuffs": [
                 {
                     "bonus_type": "AfflictedDamagePerCurse",
                     "bonus_amount": -0.06
                 }
             ]
         },
         {
             "enemy_id": "Enemy6",
             "total_hp": 9300000000.0,
             "parts": [
                 {
                     "part_id": "BodyHead",
                     "total_hp": 3348000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHead",
                     "total_hp": 3819200000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyChestUpper",
                     "total_hp": 4712000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorChestUpper",
                     "total_hp": 6683600000.0,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyArmUpperRight",
                     "total_hp": 682000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorArmUpperRight",
                     "total_hp": 852500000.0000001,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyArmUpperLeft",
                     "total_hp": 682000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorArmUpperLeft",
                     "total_hp": 852500000.0000001,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyLegUpperRight",
                     "total_hp": 1364000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorLegUpperRight",
                     "total_hp": 1432200000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyLegUpperLeft",
                     "total_hp": 1364000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorLegUpperLeft",
                     "total_hp": 1432200000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "BodyHandRight",
                     "total_hp": 682000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHandRight",
                     "total_hp": 852500000.0000001,
                     "cursed": True
                 },
                 {
                     "part_id": "BodyHandLeft",
                     "total_hp": 682000000.0,
                     "cursed": False
                 },
                 {
                     "part_id": "ArmorHandLeft",
                     "total_hp": 852500000.0000001,
                     "cursed": True
                 }
             ],
             "enemy_name": "Terro",
             "area_debuffs": [
                 {
                     "bonus_type": "AllArmorHPMult",
                     "bonus_amount": 0.1
                 }
             ],
             "cursed_debuffs": [
                 {
                     "bonus_type": "AfflictedDamagePerCurse",
                     "bonus_amount": -0.06
                 }
             ]
         }
     ],
     "area_buffs": [
         {
             "bonus_type": "ArmorDamage",
             "bonus_amount": 0.25
         }
     ]
 }
"""
