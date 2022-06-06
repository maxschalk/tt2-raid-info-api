import os

import requests
from dotenv import load_dotenv

from src.models.Stage import Stage

load_dotenv()

ENV_AUTH_SECRET = os.getenv('AUTH_SECRET')

BASE_URLS = {
    Stage.DEV: "http://localhost:5000/api/v0",
    Stage.STAGING: "https://tt2-data-staging.herokuapp.com/api/v0",
    Stage.PRODUCTION: "https://tt2-data.herokuapp.com/api/v0",
}

HEADERS = {'secret': ENV_AUTH_SECRET}


def make_request(*, method, path, data=None, stage=Stage.DEV):
    base_url = BASE_URLS[stage]

    response = method(f"{base_url}/{path}", headers=HEADERS, data=data)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return response.text

