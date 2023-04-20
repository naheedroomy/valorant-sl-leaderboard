from pydantic import BaseModel
from mongoengine import Document, StringField, ObjectIdField, ListField, BooleanField, IntField, DateTimeField, \
    FloatField
from typing import List, Optional


class Queue(BaseModel):
    queue_id: Optional[str]
    is_active: bool
    players_in_queue: List[str]


class MongoQueue(Document):
    meta = {'collection': 'queue'}
    is_active = BooleanField(required=True)
    players_in_queue = ListField(StringField())
    status = StringField(required=True)
