from typing import Optional, List

from mongoengine import Document, \
    StringField, EmailField, ObjectIdField, ListField, BooleanField, IntField, DateTimeField, FloatField
from pydantic import BaseModel, constr, EmailStr


class User(BaseModel):
    first_name: Optional[constr(min_length=1, max_length=50)]
    last_name: Optional[constr(min_length=1, max_length=50)]
    puuid: Optional[constr(min_length=1, max_length=50)]
    email: Optional[EmailStr]
    nic: Optional[constr(min_length=1, max_length=50)]
    phone: Optional[constr(min_length=1, max_length=50)]
    password: Optional[constr(min_length=4)]
    is_verified: Optional[bool]
    in_queue: Optional[bool]


class UserInQueue(BaseModel):
    queue_users: List[str]


class MongoUser(Document):
    meta = {'collection': 'user'}
    _id = ObjectIdField
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    account_name = StringField(required=True)
    account_tag = StringField(required=True)
    puuid = StringField(required=True)
    nic = StringField(required=True)
    nic_verified = BooleanField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=8)
    rank = StringField(required=False)
    phone = StringField(required=False)
    elo = IntField(required=False)
    is_verified = BooleanField(required=True, default=False)
    verify_code = IntField(required=False)
    in_queue = BooleanField(required=True, default=False)


class MongoPasswordHistory(Document):
    meta = {'collection': 'password_history'}
    user_id = ObjectIdField(required=True)
    password = StringField(required=True, min_length=8)


class MongoQueue(Document):
    meta={'collection': 'queue'}
    queue = ListField(ObjectIdField())


class MongoMatch(Document):
    selected_for_match = ListField(ObjectIdField())



class UserNew(BaseModel):
    ign: Optional[constr(min_length=1, max_length=50)]
    puuid: Optional[constr(min_length=1, max_length=50)]
    email: Optional[EmailStr]
    verification_code: Optional[constr(min_length=1, max_length=50)]
    first_name: Optional[constr(min_length=1, max_length=50)]
    last_name: Optional[constr(min_length=1, max_length=50)]

# create MongoUserNew
class MongoUserNew(Document):
    meta = {'collection': 'user_new'}
    _id = ObjectIdField
    ign = StringField(required=True)
    puuid = StringField(required=True)
    email = EmailField(required=True, unique=True)
    verification_code = StringField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)


class MongoTempUserNew(Document):
    meta = {'collection': 'user_new'}
    _id = ObjectIdField
    ign = StringField(required=True)
    puuid = StringField(required=True)
    email = EmailField(required=True, unique=True)
    verification_code = StringField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    created_at = DateTimeField(required=True)


class MongoUserLeaderBoard(Document):
    meta = {'collection': 'user_leaderboard'}
    _id = ObjectIdField
    elo = FloatField(required=True)
    rank = StringField(required=True)
    puuid = StringField(required=True, unique=True)
    riot_username = StringField(required=True)
    discord_username = StringField(required=True, unique=True)
    discord_id = IntField(required=False, default=0)
    updated_at = DateTimeField(required=False)


class UserLeaderBoard(BaseModel):
    elo: Optional[constr(min_length=1, max_length=50)]
    rank: Optional[constr(min_length=1, max_length=50)]
    puuid: Optional[constr(min_length=1, max_length=50)]
    riot_username: Optional[constr(min_length=1, max_length=50)]
    discord_username: Optional[constr(min_length=1, max_length=50)]



class DiscordRequest(BaseModel):
    discord_username: Optional[constr(min_length=1, max_length=50)]