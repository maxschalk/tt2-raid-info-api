import os

from dotenv import load_dotenv

load_dotenv()

ENV_AUTH_SECRET = os.getenv('AUTH_SECRET')

BASE_URL = "https://tt2-data.herokuapp.com/api/v0"

HEADERS = {'secret': ENV_AUTH_SECRET}


def make_request(method, path, data=None):
    response = method(f"{BASE_URL}/{path}", headers=HEADERS, data=data)

    return response.json()
