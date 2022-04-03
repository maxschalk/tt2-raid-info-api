import os
from typing import Optional, List, Tuple, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException

from src.models.raid_data import RaidSeedData, RaidDataFile
from src.utils.SortOrder import SortOrder
from src.utils.seed_data_fs_interface import (
    dump_seed_data,
    get_sorted_seed_paths,
)

load_dotenv()

ENV_AUTH_SECRET = os.getenv('AUTH_SECRET')

router = APIRouter(
    prefix="/admin",
    # tags=["raw seeds"],
    responses={404: {"description": "Not found"}},
)


def verify_authorization(secret: Optional[str]):
    if not secret or secret != ENV_AUTH_SECRET:
        raise HTTPException(
            status_code=401,
            detail=f"You are not authorized to make this request."
        )


@router.get("/all_seed_filepaths")
async def sorted_seeds(
        sort_order: Optional[SortOrder] = SortOrder.DESCENDING,
        secret: Optional[str] = Header(None)
) -> Tuple[str]:
    verify_authorization(secret=secret)

    return get_sorted_seed_paths(sort_order=sort_order)


@router.post("/add_seed")
async def sorted_seeds(
        *,
        file: RaidDataFile,
        data: List[RaidSeedData],
        secret: Optional[str] = Header(None)
) -> Dict:
    verify_authorization(secret=secret)

    filename = file.filename

    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    try:
        file_created = dump_seed_data(filename=filename, data=data)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong when interfacing with the filesystem."
        )

    if file_created is False:
        msg = f"File {filename} already exists on the server."
    else:
        msg = f"File {filename} created."

    return {
        "detail": msg,
        "file_created": file_created,
    }
