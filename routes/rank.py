import requests
from fastapi import APIRouter

rank = APIRouter(prefix="/rank",  tags=["rank"])

API_KEY = "2f691ec6ec2f2602790c812f3b1750ef17e52c48"
API_SECRET = "G9xZZh4Yx2tLc6UmQZsM"
API_ENDPOINT = "https://api.rankade.com/public/api/1"


@rank.get("/")
async def get_rating_details():
    headers1 = {
        'accept': 'application/json',
    }
    acc_details_response = requests.get(API_ENDPOINT + '/auth?key=' + API_KEY + '&secret=' + API_SECRET,
                                        headers=headers1)
    
    auth_token = acc_details_response.json()['success']['token']
    
    # add auth token to headers as Authorization bearer
    headers2 = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + auth_token,
    }

    rankings_response = requests.get(API_ENDPOINT + '/rankings', headers=headers2)

    # if rankings_response status code is 200, construct new response_json
    if rankings_response.status_code == 200:
        rankings_array = []
        for i in rankings_response.json()['success']['data']:

            response_json = {
                "team_name" : i['player']['displayName'],
                "rank": i['position'],
                "rating_points": i['ree'],
            }
            rankings_array.append(response_json)
    
    # # sort the rankings_array by the rank
    # sorted_array = rankings_array.sort(key=lambda x: x['rank'])

    return rankings_array

  
            
    
@rank.post("/match/{team1}/{team2}")
async def create_match(team1: str, team2: str):
    headers1 = {
        'accept': 'application/json',
    }
    acc_details_response = requests.get(API_ENDPOINT + '/auth?key=' + API_KEY + '&secret=' + API_SECRET,
                                        headers=headers1)
    
    auth_token = acc_details_response.json()['success']['token']
    
    # add auth token to headers as Authorization bearer
    headers2 = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + auth_token,
    }

    players_response = requests.get(API_ENDPOINT + '/players', headers=headers2)

    team1_id = ""
    team2_id = ""
    for i in range(len(players_response.json()['success']['data'])):
        if players_response.json()['success']['data'][i]['displayName'] == team1:
            team1_id = players_response.json()['success']['data'][i]['id']

    for i in range(len(players_response.json()['success']['data'])):
        if players_response.json()['success']['data'][i]['displayName'] == team2:
            team2_id = players_response.json()['success']['data'][i]['id']
    
    # get current date and time
    import datetime
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    request_json =[{
    "game": 6666,
    "weight": "normal",
    "name": team1 + " vs " + team2,
    "date": date,
    "factions": [{
        "rank": 1,
        "score": "1",
        "players": [team1_id]
    }, {
        "rank": 2,
        "score": "0",
        "players": [team2_id]  
    }],

}]  

    

    match_response = requests.post(API_ENDPOINT + '/matches/match', json=request_json, headers=headers2)
    match_response_json = match_response.json() 

    if match_response.status_code == 200:
        accepted = match_response_json['success']['acceptedCount']
        if accepted == 1:
            response_json = {
                "Match between " + team1 + " and " + team2 + " was accepted." + team1 + " is recorded as the winner."
            }
            return response_json
        else:
            return "Error, Match not created"
    
    



@rank.post("/team/{name}")
async def create_new_team(name: str):
    headers1 = {
        'accept': 'application/json',
    }
    acc_details_response = requests.get(API_ENDPOINT + '/auth?key=' + API_KEY + '&secret=' + API_SECRET,
                                        headers=headers1)
    
    auth_token = acc_details_response.json()['success']['token']
    
    # add auth token to headers as Authorization bearer
    headers2 = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + auth_token,
    }
    
    data = 'name=' + name

    players_response = requests.post(API_ENDPOINT + '/players/player', data=data, headers=headers2)
    # print("success")
    return players_response.json()


@rank.get("/api/quota")
async def get_quota():
    headers1 = {
        'accept': 'application/json',
    }
    acc_details_response = requests.get(API_ENDPOINT + '/auth?key=' + API_KEY + '&secret=' + API_SECRET,
                                        headers=headers1)

    auth_token = acc_details_response.json()['success']['token']

    # add auth token to headers as Authorization bearer
    headers2 = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + auth_token,
    }

    quota_response = requests.get(API_ENDPOINT + '/quota', headers=headers2)

    return quota_response.json()