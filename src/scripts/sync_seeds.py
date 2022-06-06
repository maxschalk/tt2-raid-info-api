import requests

from src.PATHS import RAW_SEEDS_DIR
from src.models.Stage import Stage
from src.utils.make_request import make_request
from src.utils.seed_data_fs_interface import get_all_seed_filenames


def down():
    local_seed_filenames = set(get_all_seed_filenames(dir_path=RAW_SEEDS_DIR))

    server_seed_filenames = set(
        make_request(
            method=requests.get,
            path="admin/all_seed_filenames/raw",
            stage=Stage.PRODUCTION
        )
    )

    print(local_seed_filenames, server_seed_filenames)


def up():
    # TODO Get filenames from server and upload missing
    pass
