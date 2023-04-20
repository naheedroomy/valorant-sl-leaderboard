from pydantic import BaseModel

class RiotLogin(BaseModel):
    username: str
    password: str