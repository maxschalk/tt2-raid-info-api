from src.models.SeedType import SeedType
from src.PATHS import ENHANCED_SEEDS_DIR, RAW_SEEDS_DIR


def get_seeds_dir_path(seed_type: SeedType):
    return RAW_SEEDS_DIR if seed_type == SeedType.RAW else ENHANCED_SEEDS_DIR
