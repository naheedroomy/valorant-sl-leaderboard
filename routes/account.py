import json
import os
import re
from collections import OrderedDict

import aiohttp
import cloudscraper
import requests
from fastapi import APIRouter
from urllib3 import Retry

from models.account import RiotLogin
from requests.adapters import HTTPAdapter, PoolManager
from starlette.responses import JSONResponse, Response
import redis

# Set up the Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)
user_sessions = {}
API_TOKEN = os.getenv('HENRIK_API_TOKEN')

account = APIRouter(prefix="/account", tags=["account"])

def get_build():
    url = "https://valorant-api.com/v1/version"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        riot_client_build = data["data"]["riotClientBuild"]
        return riot_client_build
    else:
        raise Exception(f"Failed to retrieve build information. Status code: {response.status_code}")

riot_client_build = get_build()

def create_sesh(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = cloudscraper.create_scraper()  # Create a CloudScraper session
    headers = OrderedDict({
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json, text/plain, */*",
        'User-Agent': f"RiotClient/{riot_client_build} rso-auth (Windows; 10;;Professional, x64)"
    })

    session.headers.update(headers)  # Update the session headers

    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=frozenset(['GET', 'POST', 'PUT']),
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

@account.post("/login/riot")
def checker(loginrequest : RiotLogin):
    successfulr1 = False
    while successfulr1 == False:
        session = create_sesh()

        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f"RiotClient/{riot_client_build} rso-auth (Windows; 10;;Professional, x64)",
        }
        r = session.post(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
        if not "html" in r.text:
            successfulr1 = True

    successfulr2 = False
    while successfulr2 == False:
        data = {
            'type': 'auth',
            'username': loginrequest.username,
            'password': loginrequest.password
        }
        r2 = session.put('https://auth.riotgames.com/api/v1/authorization',
                         json=data, headers=headers,
                         cookies=r.cookies)

        if not "html" in r.text:
            successfulr2 = True

    if not "auth_failure" in r2.text:

        if "multifactor" in r2.text:
            # Serialize the session and cookies and store them in Redis
            user_sessions_key = f"user_sessions_{loginrequest.username}"
            user_data = {
                'headers': dict(session.headers),
                'cookies': requests.utils.dict_from_cookiejar(r2.cookies)
            }
            redis_client.set(user_sessions_key, json.dumps(user_data))
            return JSONResponse(content={"status": "2FA", "username": loginrequest.username}, status_code=200)

        else:
            # print(r2.text)
            access_token = r2.json()['response']['parameters']['uri']
            access_token = access_token.split("#access_token=")[1]
            access_token = re.split(r'&', access_token)[0]

            headers = {
                'User-Agent': f"RiotClient/{riot_client_build} rso-auth (Windows; 10;;Professional, x64)",
                'Authorization': f'Bearer {access_token}',
            }
            r4 = session.post('https://entitlements.auth.riotgames.com/api/token/v1',
                              headers=headers,
                              json={},
                              cookies=r2.cookies)

            # print(r4.text)

            entitlement = r4.json()['entitlements_token']

            r5 = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})

            data = r5.json()
            puuid = data['sub']

            # print(f"Accestoken: {access_token}")
            # print("-" * 50)
            # print(f"Entitlements: {entitlement}")
            # print("-" * 50)
            # print(f"Userid: {puuid}")

            response_json = {
                "status": "success",
                "puuid": puuid,
            }

            return JSONResponse(status_code=200,
                                content=response_json)

    else:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Incorrect Username/Password"})
#
@account.post("/login/riot/2fa/{username}")
async def login_2fa(username: str, code: str):
    user_sessions_key = f"user_sessions_{username}"
    user_data = redis_client.get(user_sessions_key)

    if user_data is None:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Username not found"})


    # Deserialize the session and cookies
    user_data = json.loads(user_data)
    session = create_sesh()
    cookies = requests.utils.cookiejar_from_dict(user_data['cookies'])
    session.headers.update(user_data['headers'])

    successfulr3 = False
    while successfulr3 == False:

        data = {
            'type': 'multifactor',
            'code': code,
            'rememberDevice': True
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f"RiotClient/{riot_client_build} rso-auth (Windows; 10;;Professional, x64)",
        }
        r3 = session.put('https://auth.riotgames.com/api/v1/authorization',
                         json=data, headers=headers,
                         cookies=cookies)

        if not "html" in r3.text:
            successfulr3 = True

    if not "multifactor_attempt_failed" in r3.text:
        access_token = r3.json()['response']['parameters']['uri']
        access_token = access_token.split("#access_token=")[1]
        access_token = re.split(r'&', access_token)[0]

        headers = {
            'User-Agent': f"RiotClient/{riot_client_build} rso-auth (Windows; 10;;Professional, x64)",
            'Authorization': f'Bearer {access_token}',
        }
        r4 = session.post('https://entitlements.auth.riotgames.com/api/token/v1',
                          headers=headers,
                          json={},
                          cookies=r3.cookies)

        # print(r4.text)

        entitlement = r4.json()['entitlements_token']

        r5 = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})

        data = r5.json()
        puuid = data['sub']

        # print(f"Accestoken: {access_token}")
        # print("-" * 50)
        # print(f"Entitlements: {entitlement}")
        # print("-" * 50)
        # print(f"Userid: {puuid}")

        response_json = {
            "status": "success",
            "puuid": puuid,
        }

        redis_client.delete(user_sessions_key)
        return JSONResponse(status_code=200, content=response_json)

    else:
        # Serialize the session and cookies and store them in Redis
        user_data = {
            'headers': dict(session.headers),
            'cookies': requests.utils.dict_from_cookiejar(r3.cookies)
        }
        redis_client.set(user_sessions_key, json.dumps(user_data))
        return JSONResponse(status_code=400, content={"status": "error", "message": "Incorrect 2FA code"})


@account.get("/get/puuid/{puuid}")
async def get_account_details(puuid: str):
    async with aiohttp.ClientSession() as session:
        headers_henrik = {
            'Authorization': f'{API_TOKEN}'
        }
        async with session.get(f'https://api.henrikdev.xyz/valorant/v1/by-puuid/account/{puuid}', headers=headers_henrik) as acc_details_response:
            acc_details_json = await acc_details_response.json()
            acc_region = acc_details_json['data']['region']
            acc_name = acc_details_json['data']['name']
            acc_tag = acc_details_json['data']['tag']

        async with session.get(f'https://api.henrikdev.xyz/valorant/v1/mmr/{acc_region}/{acc_name}/{acc_tag}', headers=headers_henrik) as rank_details_response:
            rank_details_json = await rank_details_response.json()

        if rank_details_json["data"]["currenttier"] is None:
            account_json = {
                "current_tier": "Unranked",
                "rank": "Unranked",
                "small_image_url": None,
                "large_image_url": None,
                "ranking_in_tier": None,
                "mmr_change_to_last_game": None,
                "elo": 0.0,
                "name_and_tag": f"{acc_name} #{acc_tag}"
            }
        else:
            account_json = {
                "current_tier": rank_details_json["data"]["currenttier"],
                "rank": rank_details_json["data"]["currenttierpatched"],
                "small_image_url": rank_details_json["data"]["images"]["small"],
                "large_image_url": rank_details_json["data"]["images"]["large"],
                "ranking_in_tier": rank_details_json["data"]["ranking_in_tier"],
                "mmr_change_to_last_game": rank_details_json["data"]["mmr_change_to_last_game"],
                "elo": rank_details_json["data"]["elo"],
                "name_and_tag": f"{acc_name} #{acc_tag}"
            }

        return account_json