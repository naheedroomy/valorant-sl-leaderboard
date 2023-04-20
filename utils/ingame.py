import base64
import json
import os
import re
import sys

import requests
import urllib3
from prettytable import PrettyTable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

region = "ap"
pd_url = f"https://pd.{region}.a.pvp.net"
glz_url = f"https://glz-{region}-1.{region}.a.pvp.net"
headers = {}


def get_lockfile():
    try:
        with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
            data = lockfile.read().split(':')
            keys = ['name', 'PID', 'port', 'password', 'protocol']
            return dict(zip(keys, data))
    except:
        raise Exception("Lockfile not found")


lockfile = get_lockfile()
local_headers = {}
local_headers['Authorization'] = 'Basic ' + base64.b64encode(
    ('riot:' + lockfile['password']).encode()).decode()


def get_current_version():
    data = requests.get('https://valorant-api.com/v1/version')
    data = data.json()['data']
    version = f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}"
    return version


def get_headers():
    global headers
    if headers == {}:
        local_headers = {}
        local_headers['Authorization'] = 'Basic ' + base64.b64encode(
            ('riot:' + lockfile['password']).encode()).decode()
        response = requests.get(f"https://127.0.0.1:{lockfile['port']}/entitlements/v1/token", headers=local_headers,
                                verify=False)
        entitlements = response.json()
        headers = {
            'Authorization': f"Bearer {entitlements['accessToken']}",
            'X-Riot-Entitlements-JWT': entitlements['token'],
            'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
            'X-Riot-ClientVersion': get_current_version()
        }
    print(headers['X-Riot-Entitlements-JWT'])
    return headers


def get_puuid():
    local_headers = {}
    local_headers['Authorization'] = 'Basic ' + base64.b64encode(
        ('riot:' + lockfile['password']).encode()).decode()
    response = requests.get(f"https://127.0.0.1:{lockfile['port']}/entitlements/v1/token", headers=local_headers,
                            verify=False)
    entitlements = response.json()
    puuid = entitlements['subject']
    print(puuid)
    return puuid


def get_most_recent_match():
    response = requests.get(
        pd_url + f"/match-history/v1/history/{get_puuid()}?startIndex=0&endIndex=1", headers=get_headers(),
        verify=False).json()
    print(response['History'][0]['MatchID'])
    return response['History'][0]['MatchID']


get_most_recent_match()


#
#
def get_match_by_id():
    response = requests.get(
        pd_url + f"/match-details/v1/matches/{get_most_recent_match()}", headers=get_headers(), verify=False).json()
    # print(response)
    return response


get_match_by_id()


def get_name_from_puuid(puuid):
    response = requests.put(pd_url + f"/name-service/v2/players",
                            headers=get_headers(), json=[puuid], verify=False)
    # + "#" + response.json()[0]["TagLine"]
    return response.json()[0]["GameName"]


def get_party_details():
    party_req = requests.get(f"https://127.0.0.1:{lockfile['port']}/chat/v4/presences", headers=local_headers,
                             verify=False)

    party_req = party_req.json()
    private_thingy = (party_req['presences'])
    user_info = requests.get(f"https://127.0.0.1:{lockfile['port']}/rso-auth/v1/authorization/userinfo",
                             headers=local_headers, verify=False)

    user_inf = (user_info.json()['userInfo'])
    user_inf = json.loads(user_inf)
    # print(user_inf['sub'])
    pid_list = []
    for i in private_thingy:
        i['pid'] = i['pid'].split('@')[0]
        pid_list.append(i['pid'])

    element = (pid_list.index(user_inf['sub']))

    private = private_thingy[element]['private']
    private = base64.b64decode(private).decode('utf-8')
    private = json.loads(private)
    party_id = private['partyId']
    print(party_id)
    # print(private)
    return party_id


# get_party_details()


def join_party():
    # party_id = get_party_details()
    data = {
        "Subjects": ["0a6bee85-8c4b-53d4-a396-56caece16a5f"],
    }
    response = requests.post("https://glz-ap-1.ap.a.pvp.net/parties/v1/parties/bd00be1d-c4f9-4350-a4f8-bdffe669bd28/request", json=data, headers=get_headers(), verify=False)

    print(response.text)

    return response

join_party()

def get_party():
    party_id = "bd00be1d-c4f9-4350-a4f8-bdffe669bd28"
    # data = {
    #     "Subject": [""],
    # }
    response = requests.get(f"{glz_url}/parties/v1/parties/{party_id}", headers=get_headers(), verify=False)
    print(response.text)

# get_party()


def change_party_queue():
    party_id = get_party_details()
    response = requests.post(f"{glz_url}/parties/v1/parties/{party_id}/queue", headers=get_headers(), json={"queueId": "deathmatch"},
                            verify=False)
    # response = json.loads(response)
    print(response.text)

# join_party()
