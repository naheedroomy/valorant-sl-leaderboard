from fastapi import FastAPI

from routes.leaderboard import leaderboard
from routes.account import account
from routes.discord import discord_route
from routes.user import user

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()



app.include_router(account)
app.include_router(user)
app.include_router(discord_route)
app.include_router(leaderboard)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace this with the specific origin(s) you want to allow
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

