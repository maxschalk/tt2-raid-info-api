import json
import os

import requests

from src.PATHS import RAW_SEEDS_DIR
from src.models.Stage import Stage
from src.scripts.enhance_seeds import main as enhance_seeds
from src.utils.make_request import make_request
from src.utils.seed_data_fs_interface import get_all_seed_filenames, load_seed_data

import shutil


def down():
    print("syncing raid seeds down")

    server_seed_filenames = set(
        make_request(
            method=requests.get,
            path="admin/all_seed_filenames/raw",
            stage=Stage.STAGING
        )
    )

    local_seed_filenames = set(get_all_seed_filenames(dir_path=RAW_SEEDS_DIR))

    print("server:", len(server_seed_filenames))
    print("local:", len(local_seed_filenames))

    to_sync = server_seed_filenames - local_seed_filenames

    print("to sync down:", to_sync)

    for filename in to_sync:
        print(f"creating {filename}")

        response = make_request(
            method=requests.get,
            path=f"admin/raw_seed_file/{filename}",
            stage=Stage.STAGING,
            parse_response=False,
            stream=True
        )

        with open(os.path.join(RAW_SEEDS_DIR, filename), 'wb') as f:
            shutil.copyfileobj(response.raw, f)

    print("enhancing seeds")

    enhance_seeds()


def up():
    print("syncing raid seeds up")

    local_seed_filenames = set(get_all_seed_filenames(dir_path=RAW_SEEDS_DIR))

    server_seed_filenames = set(
        make_request(
            method=requests.get,
            path="admin/all_seed_filenames/raw",
            stage=Stage.STAGING
        )
    )

    print("local:", len(local_seed_filenames))
    print("server:", len(server_seed_filenames))

    to_sync = local_seed_filenames - server_seed_filenames

    print("to sync up:", to_sync)

    for filename in to_sync:
        print(f"posting {filename}")

        seed_data = load_seed_data(filepath=os.path.join(RAW_SEEDS_DIR, filename))

        response = make_request(
            method=requests.post,
            path=f"admin/raw_seed_file/{filename}",
            stage=Stage.STAGING,
            data=json.dumps(seed_data),
        )
