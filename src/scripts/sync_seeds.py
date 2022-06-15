import json
import os
import shutil
from test.utils.make_request import make_request_sync

import requests
from src.models.SeedType import SeedType
from src.models.Stage import Stage
from src.PATHS import RAW_SEEDS_DIR
from src.scripts.enhance_seeds import main as enhance_seeds
from src.utils.seed_data_fs_interface import (get_all_seed_filenames,
                                              load_seed_data)

STAGE = Stage.PRODUCTION


def down():
    print(f"syncing raid seeds down from {STAGE=}")

    server_seed_filenames = set(
        make_request_sync(
            method=requests.get,
            path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
            stage=STAGE
        )
    )

    local_seed_filenames = set(get_all_seed_filenames(dir_path=RAW_SEEDS_DIR))

    print("server:", len(server_seed_filenames))
    print("local:", len(local_seed_filenames))

    to_sync = server_seed_filenames - local_seed_filenames

    print("to sync down:", to_sync)

    for filename in to_sync:

        print(f"{filename}:")
        print(f"-- getting '{filename}'")

        response = make_request_sync(
            method=requests.get,
            path=f"admin/seed_file/{SeedType.RAW.value}/{filename}",
            stage=STAGE,
            parse_response=False,
            stream=True
        )

        if response.status_code != 200:
            print(
                f"Error when getting 'admin/seed_file/{SeedType.RAW.value}/{filename}'"
            )
            print(f"\t{response.status_code=}: {response.text}")
            continue

        print(f"-- creating {filename}")

        try:
            with open(os.path.join(RAW_SEEDS_DIR, filename), 'wb') as f:
                shutil.copyfileobj(response.raw, f)
        except Exception as e:
            print(f"Error when creating '{filename}': {e}")

        print(f"-- created '{filename}'")

    print("enhancing seeds")

    enhance_seeds()


def up():
    print(f"syncing raid seeds up to {STAGE=}")

    local_seed_filenames = set(get_all_seed_filenames(dir_path=RAW_SEEDS_DIR))

    server_seed_filenames = set(
        make_request_sync(
            method=requests.get,
            path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
            stage=STAGE
        )
    )

    print("local:", len(local_seed_filenames))
    print("server:", len(server_seed_filenames))

    to_sync = local_seed_filenames - server_seed_filenames

    print("to sync up:", to_sync)

    for filename in to_sync:
        print(f"{filename}:")
        print(f"-- loading '{filename}'")

        seed_data = load_seed_data(
            filepath=os.path.join(RAW_SEEDS_DIR, filename))

        print(f"-- posting {filename}")

        response = make_request_sync(
            method=requests.post,
            path=f"admin/raw_seed_file/{filename}",
            stage=STAGE,
            data=json.dumps(seed_data),
        )

        if response.status_code != 201:
            print(
                f"Error when posting 'admin/raw_seed_file/{filename}'"
            )
            print(f"\t{response.status_code=}: {response.text}")
            continue


def main():
    up_down = input("Sync (U)p or (D)own? Anything else aborts | U/D/* > ")

    if up_down.upper() == 'D':
        down()
        return

    if up_down.upper() == 'U':
        up()


if __name__ == "__main__":

    main()
