import logging
import sys
import requests
from hashlib import md5

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler(sys.stdout)
logger.addHandler(sh)

def nic_validator(nic):

    url = "https://sri-lankan-national-identity-card-validator.p.rapidapi.com/check/" + nic

    headers = {
        "X-RapidAPI-Key": "bd742856ebmsh5fb4e8d8b5901a0p10d8fcjsn40efb2a31c08",
        "X-RapidAPI-Host": "sri-lankan-national-identity-card-validator.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers)
        print(response.json())
        return response.json()
    except Exception as e:
        print({"error": str(e)})
        return {"error": str(e)}