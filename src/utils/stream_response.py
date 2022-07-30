import io
import json
from typing import Any

from fastapi.responses import StreamingResponse
from src.model.raid_data import map_to_native_object


def create_stream_response(*,
                           data: Any,
                           filename: str = "data") -> StreamingResponse:
    stream = io.StringIO()

    json.dump(map_to_native_object(data=data), stream)

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"})
