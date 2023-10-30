import os
import discord
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel

discord_route = APIRouter(prefix="/discord")

class DiscordUser(BaseModel):
    discord_id: str

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

async def get_user_by_id(user_id: int):
    user = None

    async def on_ready():
        nonlocal user
        try:
            user = await client.fetch_user(user_id)
        except discord.NotFound:
            user = None
        finally:
            await client.close()

    client = discord.Client(intents=intents)
    client.event(on_ready)
    await client.start(os.getenv("DISCORD_BOT_TOKEN_1"))
    print(user)
    return user

@discord_route.post("/verify_discord_id/")
async def verify_discord_id(user: DiscordUser):
    user_id = int(user.discord_id)
    discord_user = await get_user_by_id(user_id)

    if discord_user is None:
        raise HTTPException(status_code=404, detail="User not found")



    return {"discord_id": discord_user.id,
            "name": f"{discord_user.name}",
            "discriminator": f"#{discord_user.discriminator}"}
