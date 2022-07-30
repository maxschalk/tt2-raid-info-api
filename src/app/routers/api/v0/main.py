from fastapi import APIRouter
from src.domain.mongo_seed_data_repository import MongoSeedDataRepository
from src.utils.get_env import get_env
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND

from . import admin, raid_info, seeds

router = APIRouter(
    prefix="/v0",
    tags=[],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)

seed_data_repo = MongoSeedDataRepository(
    url=get_env(key="MONGO_URL"),
    username=get_env(key="MONGO_USERNAME"),
    password=get_env(key="MONGO_PASSWORD"),
    db_name=get_env(key="MONGO_DB_NAME"),
    collection_name=get_env(key="MONGO_COLLECTION_NAME"),
)

router.include_router(admin.create_router(seed_data_repo=seed_data_repo))

router.include_router(seeds.create_router(seed_data_repo=seed_data_repo))

router.include_router(raid_info.create_router(seed_data_repo=seed_data_repo))


@router.get("/", include_in_schema=False)
async def welcome():
    return {
        "message":
        "Welcome to the TT2 Raid Seed API v0! You can find the docs at /docs."
    }
