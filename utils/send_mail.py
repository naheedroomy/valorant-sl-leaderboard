import datetime
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Template
from jose import jwt

from auth.auth_handler import JWT_SECRET, JWT_ALGORITHM
from models.user import MongoUser, User
from redmail import outlook

async def send_email(receiver, code: int):

    outlook.username = os.getenv("EMAIL")
    outlook.password = os.getenv("EMAIL_PASSWORD")
    receivers = [receiver]
    outlook.send(
        receivers=receivers,
        subject="An example",
        text=f"Hi, Your verification code is :{code}"
    )


async def verify_token(token: str):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user = json.loads(MongoUser.objects(email=payload.get("email")).to_json())
    selected_user = user[0]
    return selected_user


