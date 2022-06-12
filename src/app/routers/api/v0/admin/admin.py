import os
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, Response, status
from fastapi.responses import FileResponse
from src.models.raid_data import RaidRawSeedData
from src.models.SeedType import SeedType
from src.models.SortOrder import SortOrder
from src.models.Stage import Stage
from src.PATHS import ENHANCED_SEEDS_DIR, RAW_SEEDS_DIR
from src.scripts.enhance_seeds import main as enhance_seeds
from src.utils.get_seeds_dir_path import get_seeds_dir_path
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.seed_data_fs_interface import \
    delete_raw_seed_file as fs_delete_raw_seed_file
from src.utils.seed_data_fs_interface import \
    dump_seed_data as fs_dump_seed_data
from src.utils.seed_data_fs_interface import \
    get_sorted_seed_filenames as fs_get_sorted_seed_filenames

load_dotenv()

ENV_AUTH_SECRET = os.getenv('AUTH_SECRET')
ENV_STAGE = os.getenv('STAGE')

DISPLAY_IN_DOCS = ENV_STAGE != Stage.PRODUCTION.value if ENV_STAGE else False

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)


def verify_authorization(*, secret: Optional[str]):
    if not secret or secret != ENV_AUTH_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not authorized to make this request."
        )


@router.get("/all_seed_filenames/{seed_type}", include_in_schema=DISPLAY_IN_DOCS)
async def seed_filenames(
        seed_type: SeedType,
        *,
        sort_order: Optional[SortOrder] = SortOrder.ASCENDING,
        secret: Optional[str] = Header(None)
) -> Tuple[str]:
    verify_authorization(secret=secret)

    dir_path = RAW_SEEDS_DIR if seed_type == SeedType.RAW else ENHANCED_SEEDS_DIR

    return fs_get_sorted_seed_filenames(dir_path=dir_path, sort_order=sort_order)


@router.post("/raw_seed_file/{filename}", status_code=201, include_in_schema=DISPLAY_IN_DOCS)
async def create_seed_file(
        filename: str,
        *,
        data: List[RaidRawSeedData],
        secret: Optional[str] = Header(None)
) -> Dict:
    verify_authorization(secret=secret)

    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    filepath = os.path.join(RAW_SEEDS_DIR, filename)

    try:
        file_created = fs_dump_seed_data(filepath=filepath, data=data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong when interfacing with the filesystem."
        )

    if file_created is False:
        msg = f"File '{filename}' already exists on the server."
    else:
        enhance_seeds()

        msg = f"File '{filename}' created."

    return {
        "detail": msg,
        "filename": filename,
        "created": file_created,
    }


@router.get("/seed_file/{seed_type}/{filename}", include_in_schema=DISPLAY_IN_DOCS)
async def download_raw_seed_file(seed_type: SeedType, filename: str) -> FileResponse:
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    dir_path = get_seeds_dir_path(seed_type=seed_type)

    filepath = os.path.join(dir_path, filename)

    return FileResponse(filepath, media_type='application/json', filename=filename)


@router.delete("/raw_seed_file/{filename}", include_in_schema=DISPLAY_IN_DOCS)
async def delete_raw_seed_file(
        filename: str,
        *,
        secret: Optional[str] = Header(None)
) -> Dict:
    verify_authorization(secret=secret)

    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    file_deleted = fs_delete_raw_seed_file(filename=filename)

    if file_deleted:
        enhance_seeds()
        msg = f"Raw seed file '{filename}' was deleted"
    else:
        msg = f"Raw seed file '{filename}' could not be found"

    return {
        "detail": msg,
        "filename": filename,
        "deleted": file_deleted,
    }
