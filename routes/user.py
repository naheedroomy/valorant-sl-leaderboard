from models.user import DiscordRequest
import random
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from database.db import connect_db
from models.request.user import EmailVerificationRequest
from models.user import MongoUser
from models.user import UserNew, MongoTempUserNew, UserLeaderBoard, \
    MongoUserLeaderBoard
from utils.send_mail import send_email

templates = Jinja2Templates(directory="templates")
user = APIRouter(prefix="/user")

connect_db()


@user.get('/check-ign')
async def check_ign(ign: str):
    users_ign = MongoUser.objects(account_name=ign).first()
    if users_ign:
        return JSONResponse(status_code=400, content={"message": "IGN already exists"})
    return JSONResponse(status_code=200, content={"message": "IGN is available"})


@user.get('/check-email')
async def check_email(email: str):
    users_email = MongoUser.objects(email=email).first()
    if users_email:
        return JSONResponse(status_code=400, content={"message": "Email already exists"})
    return JSONResponse(status_code=200, content={"message": "Email is available"})


@user.get('/check-discord')
async def discord(discord: DiscordRequest):
    users_email = MongoUserLeaderBoard.objects(discord_username=discord.discord_username)
    if users_email:
        return JSONResponse(status_code=400, content={"message": "Discord already exists"})
    return JSONResponse(status_code=200, content={"message": "Discord is available"})

@user.get('/check-puuid')
async def check_puuid(puuid: str):
    users_puuid = MongoUserLeaderBoard.objects(puuid=puuid)
    if users_puuid:
        return JSONResponse(status_code=400, content={"message": "Riot account already exists"})
    return JSONResponse(status_code=200, content={"message": "Riot account is available"})


@user.post('/register',
           tags=["User"])
async def create_user(user: UserNew):
    users_email = MongoUser.objects(email=user.email).first()
    users_puuid = MongoUser.objects(puuid=user.puuid).first()
    users_ign = MongoUser.objects(account_name=user.ign).first()

    if users_email:
        return JSONResponse(status_code=400, content={"message": "Email already exists"})

    if users_puuid:
        return JSONResponse(status_code=400, content={"message": "Riot account already exists"})

    if users_ign:
        return JSONResponse(status_code=400, content={"message": "IGN already exists"})

    # create a random 6 digit numerical code
    code = random.randint(000000, 999999)

    current_time = datetime.now()

    temp_created_user = MongoTempUserNew(
        first_name=user.first_name,
        last_name=user.last_name,
        ign=user.ign,
        email=user.email,
        verification_code=code,
        puuid=user.puuid,
        created_at=current_time
    )
    temp_created_user.save()
    await send_email(user.email, code)


@user.post('/verify/email/code')
async def verify_email_code(email_verification_request: EmailVerificationRequest):
    temp_user = MongoTempUserNew.objects(email=email_verification_request.email).first()

    if temp_user:
        if temp_user.verification_code == email_verification_request.code:
            # create a new user
            created_user = MongoUser(
                first_name=temp_user.first_name,
                last_name=temp_user.last_name,
                ign=temp_user.ign,
                email=temp_user.email,
                puuid=temp_user.puuid,
                is_verified=True,
            )
            created_user.save()
            temp_user.delete()
            return JSONResponse(status_code=200, content={"message": "Email verified"})
        else:
            return JSONResponse(status_code=400, content={"message": "Invalid code"})
    else:
        return JSONResponse(status_code=400, content={"message": "Email not found"})





