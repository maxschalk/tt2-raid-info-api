import os

import pytest
from dotenv import load_dotenv
from src.domain.stage import Stage

load_dotenv()


@pytest.fixture(scope="module", autouse=True)
def stage() -> Stage:
    return Stage(os.getenv("STAGE"))
