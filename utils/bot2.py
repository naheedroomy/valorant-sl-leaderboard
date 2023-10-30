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
    filename='/root/log/discord_roles.log',
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


async def update_alpha_omega_roles(member, rank):
    alpha_ranks = ['Platinum', 'Diamond', 'Immortal', 'Ascendant', 'Radiant']
    omega_ranks = ['Gold', 'Silver', 'Iron', 'Bronze']

    alpha_role = discord.utils.get(member.guild.roles, name="Alpha")
    omega_role = discord.utils.get(member.guild.roles, name="Omega")

    if rank in alpha_ranks:
        if omega_role in member.roles:
            await member.remove_roles(omega_role)
        if alpha_role not in member.roles:
            await member.add_roles(alpha_role)

    elif rank in omega_ranks:
        if alpha_role in member.roles:
            await member.remove_roles(alpha_role)
        if omega_role not in member.roles:
            await member.add_roles(omega_role)

    else:
        if alpha_role in member.roles:
            await member.remove_roles(alpha_role)
        if omega_role in member.roles:
            await member.remove_roles(omega_role)

async def update_member_roles(member, tier_icons):
    time.sleep(1.2)

    manual_role = discord.utils.get(member.guild.roles, name="Manual")
    if manual_role in member.roles:
        rank_roles = ['Ascendant', 'Diamond', 'Immortal', 'Radiant', 'Gold', 'Platinum', 'Silver', 'Iron', 'Bronze',
                      'Unranked']
        current_rank_role = next((role for role in member.roles if role.name in rank_roles), None)

        if current_rank_role:
            await update_alpha_omega_roles(member, current_rank_role.name)

        return

    discord_id = member.id
    discord_username = str(member)
    query = {"$or": [{"discord_id": discord_id}, {"discord_username": discord_username}]}
    result = collection.find_one(query)
    logging.info("Bot 2 - Processing: " + discord_username)
    if result:


        # Update discord_username in the database if discord_id exists and discord_username is different
        if "discord_id" in result and discord_id != 0 and result["discord_username"] != discord_username:
            update_query = {"discord_id": discord_id}
            new_values = {"$set": {"discord_username": discord_username}}
            logging.info(f"Updating discord_username for {discord_username} in the database.")
            collection.update_one(update_query, new_values)

        verified_role = discord.utils.get(member.guild.roles, name="Verified")
        await member.add_roles(verified_role)

        unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
        if unverified_role in member.roles:
            await member.remove_roles(unverified_role)
            logging.info(f"Removed unverified role from {discord_username}.")

        rank = result.get("rank")
        original_rank = rank
        rank = rank.split()[0]

        rank_dict = {'Iron': 'Irn', 'Bronze': 'Brz', 'Silver': 'Slv', 'Gold': 'Gld', 'Platinum': 'Plt',
                     'Diamond': 'Dia', 'Immortal': 'Imm', 'Radiant': 'Radiant', 'Ascendant': 'Asc',
                     'Unranked': 'Unranked'}

        rank_short = rank_dict[rank]
        new_nickname = f"{member.name}({rank_short})"
        if member.nick != new_nickname:
            try:
                await member.edit(nick=new_nickname)
                logging.info(f"Updated nickname - {discord_username} - {new_nickname}.")
            except discord.errors.Forbidden:
                logging.error(f"Failed to update nickname for {discord_username} due to insufficient permissions.")
                return

        if rank:
            rank_roles = ['Ascendant', 'Diamond', 'Immortal', 'Radiant', 'Gold', 'Platinum', 'Silver', 'Iron', 'Bronze',
                          'Unranked']
            current_rank_role = next((role for role in member.roles if role.name in rank_roles), None)

            if not current_rank_role or current_rank_role.name != rank:
                if current_rank_role:
                    await member.remove_roles(current_rank_role)
                    logging.info(f"Removed - {discord_username} - {current_rank_role.name}.")

                rank_role = discord.utils.get(member.guild.roles, name=rank)
                if rank_role:
                    await member.add_roles(rank_role)
                    logging.info(f"Updated - {discord_username} - {rank}.")
                else:
                    logging.error(f"Role not found for rank: {rank}")

            if rank == 'Unranked':
                manual_role = discord.utils.get(member.guild.roles, name="Manual")
                if manual_role not in member.roles:
                    await member.add_roles(manual_role)

            await update_alpha_omega_roles(member, rank)
    else:
        unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
        await member.add_roles(unverified_role)



@client2.event
async def on_member_join(member):
    time.sleep(30)
    print(f"Bot 2 - {member} has joined the server!")
    tier_icons = await fetch_tier_data()
    await update_member_roles(member, tier_icons)

@tasks.loop(minutes=45)
async def update_all_member_roles_2():
    start_time = time.time()
    tier_icons = await fetch_tier_data()
    for guild in client2.guilds:
        members = [member for member in guild.members if not member.bot]
        members_count = len(members)
        members.sort(key=lambda x: x.name)
        first_half = members[:members_count // 2 + members_count % 2]
        second_half = members[members_count // 2 + members_count % 2:]

        # Process the second half of the members
        for member in second_half:
            await update_member_roles(member, tier_icons)
    time_taken = time.time() - start_time
    logging.info(f"Bot 2 - Time taken to update all member roles: {time_taken / 60} minutes")


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

