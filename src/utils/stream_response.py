import io
import json
from typing import Any

from fastapi.responses import StreamingResponse


def create_stream_response(*,
                           data: Any,
                           filename: str = "data") -> StreamingResponse:
    stream = io.StringIO()

    json.dump(data, stream)

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"})
