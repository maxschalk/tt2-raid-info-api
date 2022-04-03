from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

SRC_DIR = ROOT_DIR.joinpath('src')

DATA_DIR = SRC_DIR.joinpath('raid_seed_data')
RAW_SEEDS_DIR = DATA_DIR.joinpath('raw_seeds')
ENHANCED_SEEDS_DIR = DATA_DIR.joinpath('enhanced_seeds')
