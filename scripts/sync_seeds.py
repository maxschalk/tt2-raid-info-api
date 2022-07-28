import json
import os
from test.utils.make_request import make_request_sync

import requests
from src.domain.seed_type import SeedType
from src.domain.stage import Stage
from src.enhance_seeds import main as enhance_seeds
from src.paths import RAW_SEEDS_DIR
from src.utils.seed_data_fs_interface import (dump_seed_data,
                                              get_all_seed_filenames,
                                              load_seed_data)

STAGE = Stage.PRODUCTION


def sync_down():
    print(f"syncing raid seeds down from {STAGE=}")

    response = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
        stage=STAGE,
        parse_response=False)

    if response.status_code != 200:
        print(
            f"Error when getting 'admin/all_seed_filenames/{SeedType.RAW.value}'"
        )
        print(f"\t{response.status_code=}: {response.text}")

        return

    data = response.json()

    server_seed_filenames = set(data)

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
            stream=True)

        if response.status_code != 200:
            print(
                f"Error when getting 'admin/seed_file/{SeedType.RAW.value}/{filename}'"
            )
            print(f"\t{response.status_code=}: {response.text}")
            continue

        print(f"-- creating {filename}")

        filepath = os.path.join(RAW_SEEDS_DIR, filename)
        data = response.json()

        try:
            dump_seed_data(filepath=filepath, data=data)
        except Exception as exc:
            print(f"Error when creating '{filename}': {exc}")

        print(f"-- created '{filename}'")

    print("enhancing seeds")

    enhance_seeds()


def sync_up():
    print(f"syncing raid seeds up to {STAGE=}")

    local_seed_filenames = set(get_all_seed_filenames(dir_path=RAW_SEEDS_DIR))

    server_seed_filenames = set(
        make_request_sync(
            method=requests.get,
            path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
            stage=STAGE))

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

        response = make_request_sync(method=requests.post,
                                     path=f"admin/raw_seed_file/{filename}",
                                     stage=STAGE,
                                     data=json.dumps(seed_data),
                                     parse_response=False)

        if response.status_code != 201:
            print(f"Error when posting 'admin/raw_seed_file/{filename}'")
            print(f"\t{response.status_code=}: {response.text}")
            continue


def main():
    up_down = input("Sync (U)p or (D)own? Anything else aborts | U/D/* > ")

    if up_down.upper() == 'D':
        return sync_down()
    if up_down.upper() == 'U':
        return sync_up()

    print(f"aborted with {up_down}")

    return None


if __name__ == "__main__":
    main()
