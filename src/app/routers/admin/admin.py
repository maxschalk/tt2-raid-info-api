import os
from typing import Optional, List, Tuple, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import FileResponse

from src.PATHS import RAW_SEEDS_DIR, ENHANCED_SEEDS_DIR
from src.models.raid_data import RaidRawSeedData
from src.utils.SortOrder import SortOrder
from src.utils.enhance_seeds import main as enhance_seeds
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.seed_data_fs_interface import (
    dump_seed_data,
    get_sorted_seed_filenames,
)

load_dotenv()

ENV_AUTH_SECRET = os.getenv('AUTH_SECRET')
ENV_STAGE = os.getenv('STAGE')

DISPLAY_IN_DOCS = ENV_STAGE != "prod" if ENV_STAGE else False

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


@router.get("/all_raw_seed_filenames", include_in_schema=DISPLAY_IN_DOCS)
async def raw_seeds_sorted(
        *,
        sort_order: Optional[SortOrder] = SortOrder.DESCENDING,
        secret: Optional[str] = Header(None)
) -> Tuple[str]:
    verify_authorization(secret=secret)

    return get_sorted_seed_filenames(dir_path=RAW_SEEDS_DIR, sort_order=sort_order)


@router.get("/all_enhanced_seed_filenames", include_in_schema=DISPLAY_IN_DOCS)
async def enhanced_seeds_sorted(
        *,
        sort_order: Optional[SortOrder] = SortOrder.DESCENDING,
        secret: Optional[str] = Header(None)
) -> Tuple[str]:
    verify_authorization(secret=secret)

    return get_sorted_seed_filenames(dir_path=ENHANCED_SEEDS_DIR, sort_order=sort_order)


@router.post("/add_raw_seed_file/{filename}", include_in_schema=DISPLAY_IN_DOCS)
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
        file_created = dump_seed_data(filepath=filepath, data=data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong when interfacing with the filesystem."
        )

    enhance_seeds()

    if file_created is False:
        msg = f"File {filename} already exists on the server."
    else:
        msg = f"File {filename} created."

    return {
        status.HTTP_201_CREATED: {
            "detail": msg,
            "file_created": file_created,
        }
    }


@router.get("/download_raw_seed_file/{filename}", include_in_schema=DISPLAY_IN_DOCS)
async def download_raw_seed_file(filename: str, ) -> FileResponse:
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    filepath = os.path.join(RAW_SEEDS_DIR, filename)

    return FileResponse(filepath, media_type='application/json', filename=filename)


@router.delete("/delete_raw_seed_file/{filename}", include_in_schema=DISPLAY_IN_DOCS)
async def delete_raw_seed_file(
        filename: str,
        *,
        secret: Optional[str] = Header(None)
) -> Dict:
    verify_authorization(secret=secret)

    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    filepath = os.path.join(RAW_SEEDS_DIR, filename)

    file_deleted = False

    if os.path.exists(filepath):
        os.remove(filepath)
        file_deleted = True

    enhance_seeds()

    if file_deleted:
        msg = f"File at ${filepath} was deleted"
    else:
        msg = f"File at ${filepath} could not be found"

    return {
        status.HTTP_200_OK: {
            "detail": msg,
            "file_deleted": file_deleted,
        }
    }
