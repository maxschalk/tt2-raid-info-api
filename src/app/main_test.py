from fastapi.testclient import TestClient
from src.stage import Stage

from .main import create_app

app = create_app(stage=Stage.TEST, seed_data_repo=None)
client = TestClient(app)


def test_routes_exist():
    expected_public_paths = {
        '/api/v0/admin/seed_identifiers/{seed_type}',
        '/api/v0/admin/seed/{seed_type}/{identifier}', '/api/v0/admin/enhance',
        '/api/v0/admin/save/{identifier}', '/api/v0/admin/delete/{identifier}',
        '/api/v0/admin/delete_old', '/api/v0/seeds/{seed_type}',
        '/api/v0/seeds/{seed_type}/recent',
        '/api/v0/raid_info/{seed_type}/{tier}/{level}'
    }

    actual_public_paths = set(app.openapi().get("paths", {}).keys())

    assert actual_public_paths == expected_public_paths

    expected_all_paths = {
        "/docs", "/redoc", "/", "/api/", "/api/v0/", *expected_public_paths
    }

    actual_all_paths = set(map(lambda r: r.path, app.routes))

    assert actual_all_paths >= expected_all_paths
