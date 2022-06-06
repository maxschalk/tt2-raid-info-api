import json

import requests

from src.models.Stage import Stage
from test.manual.base import make_request

with open(f"./test_data_20220220.json", 'r') as file:
    seed_data = json.load(file)

seed_data = [
    {
        "spawn_sequence": [
            "Takedar",
            "Lojak",
            "Lojak"
        ],
        "raid_info_valid_from": "2022-02-20T00:00:01",
        "raid_info_expire_at": "2022-02-27T00:00:00",
        "tier": "1",
        "level": "1",
        "titans": [
            {
                "enemy_id": "Enemy1",
                "total_hp": 459000.0,
                "parts": [
                    {
                        "part_id": "BodyHead",
                        "total_hp": 114750.0
                    },
                    {
                        "part_id": "BodyChestUpper",
                        "total_hp": 183600.0
                    },
                    {
                        "part_id": "BodyArmUpperRight",
                        "total_hp": 22950.0
                    },
                    {
                        "part_id": "BodyArmUpperLeft",
                        "total_hp": 22950.0
                    },
                    {
                        "part_id": "BodyLegUpperRight",
                        "total_hp": 48195.0
                    },
                    {
                        "part_id": "BodyLegUpperLeft",
                        "total_hp": 48195.0
                    },
                    {
                        "part_id": "BodyHandRight",
                        "total_hp": 22950.0
                    },
                    {
                        "part_id": "BodyHandLeft",
                        "total_hp": 22950.0
                    }
                ],
                "enemy_name": "Lojak"
            },
            {
                "enemy_id": "Enemy2",
                "total_hp": 459000.0,
                "parts": [
                    {
                        "part_id": "BodyHead",
                        "total_hp": 165240.0
                    },
                    {
                        "part_id": "BodyChestUpper",
                        "total_hp": 137700.0
                    },
                    {
                        "part_id": "BodyArmUpperRight",
                        "total_hp": 28687.5
                    },
                    {
                        "part_id": "BodyArmUpperLeft",
                        "total_hp": 28687.5
                    },
                    {
                        "part_id": "BodyLegUpperRight",
                        "total_hp": 34425.0
                    },
                    {
                        "part_id": "BodyLegUpperLeft",
                        "total_hp": 34425.0
                    },
                    {
                        "part_id": "BodyHandRight",
                        "total_hp": 28687.5
                    },
                    {
                        "part_id": "BodyHandLeft",
                        "total_hp": 28687.5
                    }
                ],
                "enemy_name": "Takedar"
            }
        ]
    },
    {
        "data": "this does not belong here",
    }
]

result = make_request(
    method=requests.post,
    path="admin/raw_seed_file/test_data_20220220.json",
    data=json.dumps(seed_data),
    stage=Stage.DEV
)

print(result)
