import os

import pytest
from dotenv import load_dotenv

from src.models.Stage import Stage

load_dotenv()


@pytest.fixture(scope="module", autouse=True)
def stage() -> Stage:
    return Stage(os.getenv("STAGE"))
