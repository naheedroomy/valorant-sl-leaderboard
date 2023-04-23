import json
import os

import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette.responses import JSONResponse

from models.user import MongoUserLeaderBoard, UserLeaderBoard

leaderboard = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

NQ_API_KEY = os.environ.get("NEATQUEUE_API")
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


@leaderboard.post('/register')
async def create_user_leaderboard(user: UserLeaderBoard):
    users_puuid = MongoUserLeaderBoard.objects(puuid=user.puuid).first()
    if users_puuid:
        return JSONResponse(status_code=400, content={"message": "Riot account already exists"})

    created_user = MongoUserLeaderBoard(
        puuid=user.puuid,
        riot_username=user.riot_username,
        discord_username=user.discord_username,
        elo=user.elo,
        rank=user.rank,
    )
    created_user.save()
    return JSONResponse(status_code=200, content={"message": "User created"})


@leaderboard.get('/show/all')
async def show_leaderboard_all():
    # sort by elo
    users = MongoUserLeaderBoard.objects().order_by('-elo')
    filtered_users = [user for user in users if user.elo != 0]
    users_json = [
        {
            'id': str(user.id),
            'discord_username': user.discord_username,
            'riot_username': user.riot_username,
            'rank': user.rank,
            'elo': user.elo
        }
        for user in filtered_users
    ]
    return JSONResponse(status_code=200, content=users_json)






@leaderboard.get('/show/top')
async def show_leaderboard_top():
    # sort by elo, and only those with elo above 1500
    users = MongoUserLeaderBoard.objects(elo__gte=1500).order_by('-elo')
    users_json = users.to_json()
    return JSONResponse(status_code=200, content=json.loads(users_json))


@leaderboard.get('/show/bottom')
async def show_leaderboard_bottom():
    # sort by elo, and only those with elo below 1500
    users = MongoUserLeaderBoard.objects(elo__lte=1500).order_by('-elo')
    users_json = users.to_json()
    return JSONResponse(status_code=200, content=json.loads(users_json))


# New endpoint with hardcoded first_id and second_id


@leaderboard.get("/alpha")
async def get_user_data():
    server_id = "1092797403301679135"
    channel_id = "1094664514877804635"
    url = f"https://api.neatqueue.com/api/leaderboard/{server_id}/{channel_id}"
    # api_key=NQ_API_KEY
    # headers = {"accept": "application/json", "Authorization": api_key}
    response = requests.get(url)

    if response.status_code == 200:
        # Process the response data
        data = response.json()
        alltime_data = data.get("alltime", [])

        # Extract the required fields and create a new JSON object
        processed_data = [
            {
                "name": item["name"].split("(")[0],
                "rank": item["data"]["rank"],
                "win_loss": f"{item['data']['wins']}-{item['data']['losses']}",
                "mmr": round(item["data"]["mmr"])
            }
            for item in alltime_data
        ]

        # Sort the processed_data array by mmr, highest to lowest
        sorted_data = sorted(processed_data, key=lambda x: x["mmr"], reverse=True)

        return JSONResponse(status_code=200, content=sorted_data)
    else:
        return JSONResponse(status_code=response.status_code, content={"message": "Error retrieving data"})


@leaderboard.get("/omega")
async def get_user_data():
    server_id = "1092797403301679135"
    channel_id = "1095085440412962896"
    url = f"https://api.neatqueue.com/api/leaderboard/{server_id}/{channel_id}"
    # api_key=NQ_API_KEY
    # headers = {"accept": "application/json", "Authorization": api_key}
    response = requests.get(url)

    if response.status_code == 200:
        # Process the response data
        data = response.json()
        alltime_data = data.get("alltime", [])

        # Extract the required fields and create a new JSON object
        processed_data = [
            {
                "name": item["name"].split("(")[0],
                "rank": item["data"]["rank"],
                "win_loss": f"{item['data']['wins']}-{item['data']['losses']}",
                "mmr": round(item["data"]["mmr"])
            }
            for item in alltime_data
        ]

        # Sort the processed_data array by rank
        sorted_data = sorted(processed_data, key=lambda x: x["rank"])

        return JSONResponse(status_code=200, content=sorted_data)
    else:
        return JSONResponse(status_code=response.status_code, content={"message": "Error retrieving data"})