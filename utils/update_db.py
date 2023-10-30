import logging
import os
import time
from datetime import datetime
import asyncio
import aiohttp
from mongoengine import Document, ObjectIdField, FloatField, StringField, connect, DateTimeField, IntField

API_TOKEN = os.getenv('HENRIK_API_TOKEN')


class MongoUserLeaderBoard(Document):
    meta = {'collection': 'user_leaderboard'}
    _id = ObjectIdField
    elo = FloatField(required=True, default=0.0)
    rank = StringField(required=True)
    puuid = StringField(required=True, unique=True)
    riot_username = StringField(required=True)
    discord_username = StringField(required=True, unique=True)
    discord_id = IntField(required=False, default=0)
    updated_at = DateTimeField(required=False)

MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST')

connect(host=f"mongodb+srv://naheedroomy:{MONGO_PASSWORD}@{MONGO_HOST}?retryWrites=true&w=majority")

logging.basicConfig(
    filename='/root/log/update.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

async def update_all_users():
    count = 0
    now_1 = datetime.now()
    dt_string_1 = now_1.strftime("%d/%m/%Y %H:%M:%S")
    logging.info(f"-----------------------------------------------------")
    logging.info(f"Updating Leaderboard: Started at {dt_string_1}")
    users = MongoUserLeaderBoard.objects
    headers = {
        'Authorization': f'{API_TOKEN}'
    }
    for user in users:
        time.sleep(2)
        user_puuid = user.puuid
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://api.henrikdev.xyz/valorant/v1/by-puuid/account/{user_puuid}', headers=headers) as acc_details_response:
                acc_details_json = await acc_details_response.json()
                acc_region = acc_details_json['data']['region']
                acc_name = acc_details_json['data']['name']
                acc_tag = acc_details_json['data']['tag']

            async with session.get(
                    f'https://api.henrikdev.xyz/valorant/v1/mmr/{acc_region}/{acc_name}/{acc_tag}', headers=headers) as rank_details_response:
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

        # get current date and time
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        obtained_user = MongoUserLeaderBoard.objects(puuid=user_puuid).first()
        obtained_user.elo = account_json["elo"]
        obtained_user.rank = account_json["rank"]
        obtained_user.riot_username = account_json["name_and_tag"]
        obtained_user.updated_at = dt_string

        obtained_user.save()
        count += 1

        # Check if discord_username ends with #0
        if obtained_user.discord_username.endswith('#0'):
            obtained_user.discord_username = obtained_user.discord_username.rstrip(
                '#0')  # Remove #0 from discord_username
            obtained_user.save()

    logging.info(f"Users updated: {count}")


async def run_periodically():
    while True:
        try:
            await update_all_users()
            await asyncio.sleep(900)  # 15 minutes in seconds
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            await asyncio.sleep(60)  # Wait for 1 minute before retrying in case of an error

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(run_periodically())
        except Exception as e:
            logging.error(f"Error occurred in main loop: {e}")
            time.sleep(60)  # Wait for 1 minute before restarting the main loop in case of an error
