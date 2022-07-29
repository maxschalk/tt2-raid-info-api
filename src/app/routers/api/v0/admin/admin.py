import io
import json
import os
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, StreamingResponse
from src.model.raid_data import RaidSeedDataEnhanced, RaidSeedDataRaw
from src.model.seed_type import SeedType
from src.paths import ENHANCED_SEEDS_DIR, RAW_SEEDS_DIR
from src.scripts.enhance_seeds import enhance_raid_info
from src.scripts.enhance_seeds import main as enhance_seeds
from src.seed_data_fs_interface import dump_seed_data as fs_dump_seed_data
from src.seed_data_fs_interface import fs_delete_raw_seed_file
from src.seed_data_fs_interface import \
    get_sorted_seed_filenames as fs_get_sorted_seed_filenames
from src.utils.get_seeds_dir_path import get_seeds_dir_path
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.sort_order import SortOrder

load_dotenv()

ENV_AUTH_SECRET = os.getenv('AUTH_SECRET')
ENV_STAGE = os.getenv('STAGE')

DISPLAY_IN_DOCS = True  # ENV_STAGE != Stage.PRODUCTION.value if ENV_STAGE else False

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)


def verify_authorization(*, secret: Optional[str]):
    if not secret or secret != ENV_AUTH_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to make this request.")


@router.get("/seed_identifiers/{seed_type}", include_in_schema=DISPLAY_IN_DOCS)
async def get_seed_identifiers(
    seed_type: SeedType,
    *,
    sort_order: Optional[SortOrder] = SortOrder.ASCENDING,
) -> Tuple[str]:

    dir_path = RAW_SEEDS_DIR if seed_type == SeedType.RAW else ENHANCED_SEEDS_DIR

    return fs_get_sorted_seed_filenames(dir_path=dir_path,
                                        sort_order=sort_order)


@router.get("/seed/{seed_type}/{identifier}",
            include_in_schema=DISPLAY_IN_DOCS)
async def download_seed_file(seed_type: SeedType,
                             identifier: str) -> FileResponse:
    if not identifier.endswith(".json"):
        identifier = f"{identifier}.json"

    dir_path = get_seeds_dir_path(seed_type=seed_type)

    filepath = os.path.join(dir_path, identifier)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{seed_type.value} file {identifier} does not exist")

    try:
        return FileResponse(filepath,
                            media_type='application/json',
                            filename=f"{seed_type.value}_{identifier}")

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong when getting the file: {exc}"
        ) from exc


@router.post("/enhance", include_in_schema=DISPLAY_IN_DOCS)
async def enhance_seed(
    *,
    download: bool = False,
    data: List[RaidSeedDataRaw],
) -> List[RaidSeedDataEnhanced]:

    enhanced_seed_data = list(map(enhance_raid_info, jsonable_encoder(data)))

    if download:
        stream = io.StringIO()

        json.dump(enhanced_seed_data, stream)

        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="application/json",
            headers={
                "Content-Disposition":
                "attachment; filename=enhanced_custom_seed.json"
            })

    return enhanced_seed_data


@router.post("/save/{identifier}",
             status_code=201,
             include_in_schema=DISPLAY_IN_DOCS)
async def save_seed(
    identifier: str,
    *,
    data: List[RaidSeedDataRaw],
    secret: Optional[str] = Header(None)) -> Dict:
    verify_authorization(secret=secret)

    if not identifier.endswith(".json"):
        identifier = f"{identifier}.json"

    filepath = os.path.join(RAW_SEEDS_DIR, identifier)

    try:
        file_created = fs_dump_seed_data(filepath=filepath, data=data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong when interfacing with the filesystem."
        ) from exc

    if file_created is False:
        msg = f"File '{identifier}' already exists on the server."
    else:
        enhance_seeds()

        msg = f"File '{identifier}' created."

    return {
        "detail": msg,
        "filename": identifier,
        "created": file_created,
    }


@router.delete("/delete/{identifier}", include_in_schema=DISPLAY_IN_DOCS)
async def delete_seed(identifier: str, *,
                      secret: Optional[str] = Header(None)) -> Dict:
    verify_authorization(secret=secret)

    if not identifier.endswith(".json"):
        identifier = f"{identifier}.json"

    file_deleted = fs_delete_raw_seed_file(filename=identifier)

    if file_deleted:
        enhance_seeds()
        msg = f"Raw seed file '{identifier}' was deleted"
    else:
        msg = f"Raw seed file '{identifier}' could not be found"

    return {
        "detail": msg,
        "filename": identifier,
        "deleted": file_deleted,
    }
