import json
from test.utils.make_request import make_request_sync

import requests
from src.domain.filesystem_seed_data_repository import \
    FSSeedDataRepository
from src.model.seed_type import SeedType
from src.paths import DATA_DIR
from src.scripts.enhance_seeds import main as enhance_seeds
from src.stage import Stage

STAGE = Stage.PRODUCTION

seed_data_repo = FSSeedDataRepository(base_path=DATA_DIR)


def sync_down():
    print(f"syncing raid seeds down from {STAGE=}")

    server_seed_ids = set(
        make_request_sync(method=requests.get,
                          path=f"admin/seed_identifiers/{SeedType.RAW.value}",
                          stage=STAGE))

    local_seed_ids = set(seed_data_repo.list_seed_identifiers())

    print("server:", len(server_seed_ids))
    print("local:", len(local_seed_ids))

    to_sync = server_seed_ids - local_seed_ids

    print("to sync down:", to_sync)

    for seed_id in to_sync:

        print(f"{seed_id}:")
        print(f"-- getting '{seed_id}'")

        response = make_request_sync(
            method=requests.get,
            path=f"admin/seed/{SeedType.RAW.value}/{seed_id}",
            stage=STAGE,
            parse_response=False,
            stream=True)

        if response.status_code != 200:
            print(
                f"Error when getting 'admin/seed/{SeedType.RAW.value}/{seed_id}'"
            )
            print(f"\t{response.status_code=}: {response.text}")
            continue

        print(f"-- creating {seed_id}")

        data = response.json()
        seed_data_repo.save_seed(identifier=seed_id,
                                 seed_type=SeedType.RAW,
                                 data=data)

        print(f"-- created '{seed_id}'")

    print("enhancing seeds")

    enhance_seeds()


def sync_up():
    print(f"syncing raid seeds up to {STAGE=}")

    server_seed_ids = set(
        make_request_sync(method=requests.get,
                          path=f"admin/seed_identifiers/{SeedType.RAW.value}",
                          stage=STAGE))

    local_seed_ids = set(seed_data_repo.list_seed_identifiers())

    print("local:", len(local_seed_ids))
    print("server:", len(server_seed_ids))

    to_sync = local_seed_ids - server_seed_ids

    print("to sync up:", to_sync)

    for seed_id in to_sync:
        print(f"{seed_id}:")
        print(f"-- loading '{seed_id}'")

        seed_data = seed_data_repo.get_seed_by_identifier(
            identifier=seed_id, seed_type=SeedType.RAW)

        print(f"-- posting {seed_id}")

        response = make_request_sync(method=requests.post,
                                     path=f"admin/save/{seed_id}",
                                     stage=STAGE,
                                     data=json.dumps(seed_data),
                                     parse_response=False)

        if response.status_code != 201:
            print(f"Error when posting 'admin/raw_seed_file/{seed_id}'")
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
