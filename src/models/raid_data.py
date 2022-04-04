from typing import List

from pydantic import BaseModel

from src.models.titan_anatomy import TitanAnatomy


class RaidDataFile(BaseModel):
    filename: str


class Buff(BaseModel):
    bonus_type: str
    bonus_amount: float


class Titan(BaseModel):
    enemy_id: str
    enemy_name: str

    total_hp: float
    parts: List

    area_debuffs: List[Buff] = None
    cursed_debuffs: List[Buff] = None


class TitanPart(BaseModel):
    part_id: TitanAnatomy
    total_hp: float
    cursed: bool


class RaidRawSeedData(BaseModel):
    spawn_sequence: List[str]

    raid_info_valid_from: str
    raid_info_expire_at: str

    tier: int
    level: int

    titans: List[Titan]

    area_buffs: List[Buff] = None


class EnhancedTitanPart(TitanPart):
    total_hp_formatted: str


class ConsolidateditanPart(BaseModel):
    part_id: TitanAnatomy

    armor_hp: int | float
    body_hp: int | float

    armor_cursed: bool
    body_cursed: bool


class EnhancedTitan(Titan):
    total_armor_hp: int | float
    total_armor_hp_formatted: str

    total_body_hp: int | float
    total_body_hp_formatted: str

    skippable_hp: int | float
    skippable_hp_formatted: str

    consolidated_parts: List[ConsolidateditanPart]

    cursed_parts: List[EnhancedTitanPart]
    number_of_cursed_parts: int


class RaidEnhancedSeedData(RaidRawSeedData):
    raid_total_target_hp: int | float
    raid_total_target_hp_formatted: str

    titans: List[EnhancedTitan]


RaidSeedData = RaidRawSeedData | RaidEnhancedSeedData

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
