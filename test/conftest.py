import pytest
from src.stage import Stage
from src.utils.get_env import get_env


@pytest.fixture(scope="module", autouse=True)
def stage() -> Stage:
    return Stage(get_env(key='STAGE', strict=False) or Stage.PRODUCTION)
