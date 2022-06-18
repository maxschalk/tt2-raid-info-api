from pathlib import Path

from src.models.SeedType import SeedType

ROOT_DIR = Path(__file__).parent.parent

SRC_DIR = ROOT_DIR.joinpath('src')

DATA_DIR = ROOT_DIR.joinpath('db')
RAW_SEEDS_DIR = DATA_DIR.joinpath(SeedType.RAW.value)
ENHANCED_SEEDS_DIR = DATA_DIR.joinpath(SeedType.ENHANCED.value)
