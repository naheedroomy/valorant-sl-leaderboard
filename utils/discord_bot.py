import logging
import os
import time

import aiohttp
import discord
import pymongo
from discord.ext import tasks

# Define intents
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

# Set up connection to MongoDB
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST')
DISCORD_BOT_TOKEN_1 = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_BOT_TOKEN_2 = os.getenv('DISCORD_BOT_TOKEN_2')
DISCORD_BOT_TOKEN_3 = os.getenv('DISCORD_BOT_TOKEN_3')
BOT_NUMBER = int(os.getenv('BOT_NUMBER'))

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


async def generate_user_message(guild):
    verified_role = discord.utils.get(guild.roles, name="Verified")
    verified_members = [m for m in guild.members if verified_role in m.roles and not m.bot]

    user_message = ""

    for member in verified_members:
        discord_username = str(member)

        query = {"discord_username": discord_username}
        result = collection.find_one(query)

        if result:
            riot_id = result.get("riot_username")
            discord_username = discord_username.split("#")[0]
            user_message += f"{discord_username} --> {riot_id}\n"
        else:
            logging.warning(f"No database entry found for: {discord_username}")

    return user_message


@tasks.loop(minutes=5)
async def update_user_message():
    for guild in client.guilds:
        channel = client.get_channel(1095889534111203448)
        if not channel:
            logging.error("Channel not found.")
            continue

        message = await generate_user_message(guild)

        # Split the message into multiple parts without cutting names
        message_parts = []
        while len(message) > 2000:
            split_index = message[:2000].rfind('\n')
            message_parts.append(message[:split_index])
            message = message[split_index+1:]
        message_parts.append(message)

        # Search for the bot's last messages in the channel
        bot_messages = []
        async for m in channel.history(limit=10):
            if m.author == client.user:
                bot_messages.append(m)

        # Delete old bot messages if there are more messages than message parts
        if len(bot_messages) > len(message_parts):
            for i in range(len(message_parts), len(bot_messages)):
                await bot_messages[i].delete()

        # If a bot message was found, edit it. Otherwise, send a new message.
        for i, message_part in enumerate(message_parts):
            if i < len(bot_messages):
                await bot_messages[i].edit(content=message_part)
            else:
                await channel.send(message_part)



@update_user_message.before_loop
async def before_update_user_message():
    await client.wait_until_ready()

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


@client.event
async def on_member_join(member):
    tier_icons = await fetch_tier_data()
    await update_member_roles(member, tier_icons)


# Create a lock to prevent overlapping tasks

@tasks.loop(minutes=30)
async def update_all_member_roles():
    tier_icons = await fetch_tier_data()
    for guild in client.guilds:
        members = [member for member in guild.members if not member.bot]
        members_count = len(members)

        # Divide the members between the bots
        members_third = members_count // 3
        if BOT_NUMBER == 1:
            members_to_process = members[:members_third]
        elif BOT_NUMBER == 2:
            members_to_process = members[members_third:2*members_third]
        else:  # BOT_NUMBER == 3
            members_to_process = members[2*members_third:]

        for member in members_to_process:
            await update_member_roles(member, tier_icons)


@update_all_member_roles.before_loop
async def before_update_all_member_roles():
    await client.wait_until_ready()


@client.event
async def on_ready():
    update_all_member_roles.start()
    update_user_message.start()


if BOT_NUMBER == 1:
    client.run(DISCORD_BOT_TOKEN_1)
elif BOT_NUMBER == 2:
    client.run(DISCORD_BOT_TOKEN_2)
elif BOT_NUMBER == 3:
    client.run(DISCORD_BOT_TOKEN_3)