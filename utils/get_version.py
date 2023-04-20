import requests
from starlette.responses import JSONResponse


def get_client_version():
    response = requests.get('https://valorant-api.com/v1/version')
    print(response.json())
    return JSONResponse(status_code=200, content=response.json()['data']['riotClientVersion'])


get_client_version()