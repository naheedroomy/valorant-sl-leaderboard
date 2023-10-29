import os
from mongoengine import connect, disconnect

def connect_db():
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_HOST = os.getenv('MONGO_HOST')
    connection_str = f"mongodb://naheedroomy:{MONGO_PASSWORD}@{MONGO_HOST}/?retryWrites=true&w=majority"
    print(connection_str)
    connect(host=connection_str)

def disconnect_db():
    disconnect()