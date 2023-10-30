import logging
import os
import time
import asyncio
import aiohttp
import discord
from discord.ext import tasks
import pymongo

# Define intents
intents = discord.Intents.default()
intents.members = True

client2 = discord.Client(intents=intents)


# Set up connection to MongoDB
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST')
DISCORD_BOT_TOKEN_1 = os.getenv('DISCORD_BOT_TOKEN_1')
DISCORD_BOT_TOKEN_2 = os.getenv('DISCORD_BOT_TOKEN_2')

logging.basicConfig(
    filename='/root/log/discord_usernames.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

mongo_client = pymongo.MongoClient(
    f"mongodb+srv://naheedroomy:{MONGO_PASSWORD}@{MONGO_HOST}?retryWrites=true&w=majority")
db = mongo_client["live"]
collection = db["user_leaderboard"]


async def fetch_tier_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://valorant-api.com/v1/competitivetiers') as response:
            if response.status == 200:
                data = await response.json()
                tiers = data['data'][0]['tiers']
                tier_icons = {tier['tierName']: tier['smallIcon'] for tier in tiers if tier['smallIcon']}
                return tier_icons
            else:
                logging.error(f"Failed to fetch tier data: {response.status}")
                return {}


def update_member_roles(member, tier_icons):
    time.sleep(1.2)

    discord_username = str(member)
    discord_id = member.id
    print(f'Discord Username: {discord_username}')
    print(f'Discord ID: {discord_id}')
    print(f'................................................................................')


@tasks.loop(minutes=30)
async def update_all_member_roles_2():
    count = 0
    start_time = time.time()
    tier_icons = await fetch_tier_data()
    for guild in client2.guilds:
        members = [member for member in guild.members if not member.bot]

        # Process the second half of the members
        for member in members:
            update_member_roles(member, tier_icons)
            count += 1


@update_all_member_roles_2.before_loop
async def before_update_all_member_roles_2():
    await client2.wait_until_ready()


# Define a second on_ready event for the second bot
@client2.event
async def on_ready():
    update_all_member_roles_2.start()
    print(f'{client2.user} has connected to Discord!')


# Run the main function in an async context
client2.run(DISCORD_BOT_TOKEN_2)

