from src.PATHS import RAW_SEEDS_DIR, ENHANCED_SEEDS_DIR
from src.utils.seed_data_fs_interface import get_all_seed_filenames


# TODO


def main():
    raw_seed_paths = set(get_all_seed_filenames(dir_path=RAW_SEEDS_DIR))
    enhanced_seed_paths = set(get_all_seed_filenames(dir_path=ENHANCED_SEEDS_DIR))

    delete_seed_filenames = enhanced_seed_paths - raw_seed_paths

    enhance_seed_filenames = raw_seed_paths - enhanced_seed_paths


if __name__ == '__main__':
    main()
