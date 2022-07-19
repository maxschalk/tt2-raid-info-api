from fastapi import status

RESPONSE_STANDARD_NOT_FOUND = {
    status.HTTP_404_NOT_FOUND: {
        "detail": "Path not found"
    }
}
