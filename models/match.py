from pydantic import BaseModel
from mongoengine import Document, StringField, ObjectIdField, ListField, BooleanField, IntField, DateTimeField, FloatField
from typing import List


class Match(BaseModel):
    match_id: str
    players: List[str]
    team_1: List[str]
    team_2: List[str]
    team_1_cap: str
    team_2_cap: str


class MongoMatch(Document):
    meta = {'collection': 'match'}
    match_id = StringField(required=True)
    players = ListField(StringField())
    team_1 = ListField(StringField(required=False))
    team_2 = ListField(StringField(required=False))
    team_1_cap = StringField(required=False)
    team_2_cap = StringField(required=False)

