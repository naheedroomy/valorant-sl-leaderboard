import os
from mongoengine import connect, disconnect

def connect_db():
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_HOST = os.getenv('MONGO_HOST')
    connect(host=f"mongodb+srv://naheedroomy:{MONGO_PASSWORD}@{MONGO_HOST}?retryWrites=true&w=majority")

def disconnect_db():
    disconnect()