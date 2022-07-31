from enum import Enum


class Stage(Enum):
    TEST = "test"
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"
